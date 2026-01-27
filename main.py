# from fastapi import FastAPI, UploadFile, File
# from fastapi.middleware.cors import CORSMiddleware
# import chunk

# app = FastAPI()

# origin = [
#     "http://localhost:3000",
# ]

# # Pour autoriser React à communiquer avec FastAPI
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origin,  # autorise toutes les origines pour dev
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# # Route POST pour recevoir un PDF
# @app.post("/upload")
# async def upload_pdf(file: UploadFile = File(...)):
#     # Affiche le nom du fichier reçu
#     print(f"Nom du fichier reçu : {file.filename}")
    
#     # Lire le contenu (optionnel)
#     # content = await file.read()
#     # print(f"Taille du fichier : {len(content)} bytes")
    
#     # Ici tu pourrais appeler ta fonction Python sur le PDF
#     text = chunk.pdfReader(file.filename)
#     chunks = chunk.chunk_text(text)

#     chunk_embeddings = []
#     for chunnk in chunks:
#         emb = ollama.embeddings(
#             model="nomic-embed-text",
#             prompt=chunnk
#         )["embedding"]
#         chunk_embeddings.append(np.array(emb))
    
#     reranker = CrossEncoder("BAAI/bge-reranker-large")
#     res = chunk.main_loop(chunk_embeddings, chunk.QUESTION_RAG)
#     q_r = []
#     for key, value in res.items():
#         q_r.append({
#             "question": key,
#             "réponse": value
#         })

#     # result = f"PDF '{file.filename}' reçu avec succès !"
    
#     return q_r

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil
import tempfile
import os
import chunk
import numpy as np
import ollama

app = FastAPI(title="ALU/ADA GPT - RAG PDF")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Ajout du port Vite par défaut
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    # Validation du type de fichier
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Seuls les fichiers PDF sont acceptés")
    
    # Validation de la taille (max 50MB)
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Fichier trop volumineux (max 50MB)")
    
    # Création d'un fichier temporaire (compatible Windows/Linux/Mac)
    temp_file = None
    try:
        # Créer un fichier temporaire avec extension .pdf
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        
        # 2️⃣ Lecture PDF
        text = chunk.pdfReader(temp_file_path)

        # 3️⃣ Chunking
        chunks = chunk.chunk_text(text)

        # 4️⃣ Embeddings
        chunk_embeddings = []
        for c in chunks:
            emb = ollama.embeddings(
                model="nomic-embed-text",
                prompt=c
            )["embedding"]
            chunk_embeddings.append(np.array(emb))

        # 5️⃣ RAG - Correction: utiliser questions_rag au lieu de QUESTION_RAG
        res = chunk.main_loop(chunk_embeddings, chunk.questions_rag, chunks)

        # 6️⃣ Format React-friendly
        q_r = []
        for key, value in res.items():
            q_r.append({
                "question": key,
                "reponse": value
            })

        return q_r
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du traitement: {str(e)}")
    
    finally:
        # Nettoyage du fichier temporaire
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception:
                pass  # Ignorer les erreurs de suppression



