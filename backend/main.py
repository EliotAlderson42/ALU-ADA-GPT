from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from backend.create_dc1 import create_dc1, fill_dc1
import tempfile
import os
import sys
import backend.chunk as chunk
import backend.database as db
import numpy as np
import ollama

app = FastAPI(title="ALU/ADA GPT - RAG PDF")


class QuestionCreate(BaseModel):
    llm: str
    rerank: str
    user: str
    keyword: str


class QuestionUpdate(BaseModel):
    llm: str | None = None
    rerank: str | None = None
    user: str | None = None
    keyword: str | None = None


class AskBody(BaseModel):
    question: str
    keyword: str = ""
    rerank: str = ""


# Dernier PDF traité : embeddings et chunks pour les questions supplémentaires (page Réponses)
_last_upload_embeddings = None
_last_upload_chunks = None


@app.on_event("startup")
def startup():
    db.init_db()
    print("[BACKEND] Démarré. POST /upload, GET /questions, etc. sur http://127.0.0.1:8000", flush=True)


@app.get("/health")
def health():
    """Vérifie que le backend répond (utilisé par le proxy / front)."""
    return {"status": "ok"}


@app.get("/questions")
def list_questions():
    """Liste toutes les questions RAG (pour l'analyse des PDF)."""
    return db.get_all_questions()


@app.post("/questions")
def create_question(body: QuestionCreate):
    """Ajoute une nouvelle question RAG."""
    return db.add_question(llm=body.llm, rerank=body.rerank, user=body.user, keyword=body.keyword)


@app.delete("/questions/{question_id}")
def delete_question(question_id: int):
    """Supprime une question par id."""
    if not db.delete_question(question_id):
        raise HTTPException(status_code=404, detail="Question introuvable")
    return {"ok": True}


@app.get("/members")
def list_members():
    """Liste tous les membres enregistrés."""
    return db.get_all_members()


@app.post("/members")
def create_member(body: dict):
    """Enregistre un membre. Body: { lotNumero?, identification?, prestations? }"""
    lot = body.get("lotNumero", "")
    ident = body.get("identification", "")
    prest = body.get("prestations", "")
    return db.add_member(lot_numero=lot, identification=ident, prestations=prest)


@app.delete("/members/{member_id}")
def delete_member(member_id: int):
    """Supprime un membre par id."""
    if not db.delete_member(member_id):
        raise HTTPException(status_code=404, detail="Membre introuvable")
    return {"ok": True}


@app.get("/mandataires")
def list_mandataires():
    """Liste tous les mandataires enregistrés."""
    return db.get_all_mandataires()


@app.post("/mandataires")
def create_mandataire(body: dict):
    """Enregistre un mandataire. Body: champs CandidateInfo (camelCase)."""
    return db.add_mandataire(
        nom_commercial_denomination=body.get("nomCommercialDenomination", ""),
        adresses_postale_siege=body.get("adressesPostaleSiege", ""),
        adresse_electronique=body.get("adresseElectronique", ""),
        telephone_telecopie=body.get("telephoneTelecopie", ""),
        siret_ou_identification=body.get("siretOuIdentification", ""),
    )


@app.delete("/mandataires/{mandataire_id}")
def delete_mandataire_route(mandataire_id: int):
    """Supprime un mandataire par id."""
    if not db.delete_mandataire(mandataire_id):
        raise HTTPException(status_code=404, detail="Mandataire introuvable")
    return {"ok": True}


@app.get("/dc2/operateurs")
def list_dc2_operateurs():
    """Liste tous les opérateurs enregistrés (Module H DC2)."""
    return db.get_all_dc2_operateurs()


@app.post("/dc2/operateurs")
def create_dc2_operateur(body: dict):
    """Enregistre un opérateur. Body: { lotNumero?, nomMembreGroupement?, identification? }"""
    return db.add_dc2_operateur(
        lot_numero=body.get("lotNumero", ""),
        nom_membre_groupement=body.get("nomMembreGroupement", ""),
        identification=body.get("identification", ""),
    )


@app.delete("/dc2/operateurs/{operateur_id}")
def delete_dc2_operateur_route(operateur_id: int):
    """Supprime un opérateur par id."""
    if not db.delete_dc2_operateur(operateur_id):
        raise HTTPException(status_code=404, detail="Opérateur introuvable")
    return {"ok": True}


@app.put("/questions/{question_id}")
def update_question(question_id: int, body: QuestionUpdate):
    """Met à jour une question (champs optionnels)."""
    updated = db.update_question(
        question_id,
        llm=body.llm,
        rerank=body.rerank,
        user=body.user,
        keyword=body.keyword,
    )
    if updated is None:
        raise HTTPException(status_code=404, detail="Question introuvable")
    return updated


@app.post("/dc1")
def create_dc1_submit(body: dict):
    """
    Reçoit toutes les données de la page DC1 (modules A/B, C, D, E, F, G).
    Retourne les données reçues pour confirmation ; le backend peut ensuite
    générer un document (Word, etc.) ou les stocker.
    """
    data = create_dc1(body)
    fill_dc1(data)
    return {"ok": True, "data": body}


@app.get("/dc1/download")
def download_dc1():
    """Télécharge le document DC1 généré (dc1.docx)."""
    path = os.path.join(os.path.dirname(__file__), "output", "dc1.docx")
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="Document DC1 non trouvé. Créez-le d'abord via « Créer DC1 ».")
    return FileResponse(path, filename="dc1.docx", media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")


@app.post("/ask")
def ask_supplementary(body: AskBody):
    """
    Pose une question au LLM concernant le dernier PDF uploadé.
    Appelle chunk.add_question(question, keyword, rerank, embeddings, chunks).
    Utilisé par la fenêtre chat de la page Réponses.
    """
    global _last_upload_embeddings, _last_upload_chunks
    if _last_upload_embeddings is None or _last_upload_chunks is None:
        raise HTTPException(
            status_code=400,
            detail="Aucun PDF n'a encore été analysé. Uploadez un PDF depuis la page d'accueil puis revenez sur les résultats.",
        )
    question = (body.question or "").strip()
    if not question:
        raise HTTPException(status_code=400, detail="La question ne peut pas être vide.")
    keyword = (body.keyword or "").strip() or "_supplement_"
    rerank_q = (body.rerank or "").strip() or question
    try:
        answer = chunk.add_question(question, keyword, rerank_q, _last_upload_embeddings, _last_upload_chunks)
        return {"reponse": answer}
    except Exception as e:
        import traceback
        print("[BACKEND] Erreur /ask:", repr(e), flush=True)
        print(traceback.format_exc(), flush=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/questions/sync-from-default")
def sync_questions_from_default():
    """
    Remplace toutes les questions en base par la liste questions_rag de chunk.py.
    Utile pour resynchroniser la base avec le code quand tu as modifié questions_rag.
    """
    return db.sync_from_default_questions()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    print("[BACKEND] Upload reçu:", file.filename, flush=True)
    sys.stdout.flush()
    sys.stderr.flush()

    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Seuls les fichiers PDF sont acceptés")
    
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Fichier trop volumineux (max 50MB)")
    
    temp_file = None
    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        
        text = chunk.pdfReader(temp_file_path)

        # Chunks par clustering K-means (phrases → embeddings → clusters) ou par fenêtre glissante
        chunks = chunk.chunk_text(text)

        chunk_embeddings = []
        for c in chunks:
            emb = ollama.embeddings(
                model="nomic-embed-text",
                prompt=c["text"]
            )["embedding"]
            chunk_embeddings.append(np.array(emb))

        questions_rag = db.get_all_questions()
        questions_rag = [
            {"llm": q["llm"], "rerank": q["rerank"], "user": q["user"], "keyword": q["keyword"]}
            for q in questions_rag
        ]
        res, data = chunk.main_loop(chunk_embeddings, questions_rag, chunks)

        q_r = []
        for key, value in res.items():
            q_r.append({
                "question": key,
                "reponse": value
            })

        # Stocker pour les questions supplémentaires sur la page Réponses
        global _last_upload_embeddings, _last_upload_chunks
        _last_upload_embeddings = chunk_embeddings
        _last_upload_chunks = chunks

        # q_r pour affichage, data pour sauvegarde (future page Word, etc.)
        return {"questions": q_r, "data": data}
    
    except Exception as e:
        import traceback
        print("[BACKEND] Erreur pendant /upload:", repr(e), flush=True)
        print(traceback.format_exc(), flush=True)
        raise HTTPException(status_code=500, detail=f"Erreur lors du traitement: {str(e)}")
    
    finally:
        # Nettoyage du fichier temporaire
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception:
                pass  # Ignorer les erreurs de suppression



