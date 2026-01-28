from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil
import tempfile
import os
import backend.chunk as chunk
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
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Seuls les fichiers PDF sont acceptés")
    
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Fichier trop volumineux (max 50MB)")
    
    temp_file = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        
        text = chunk.pdfReader(temp_file_path)

        chunks = chunk.chunk_text(text)

        chunk_embeddings = []
        for c in chunks:
            emb = ollama.embeddings(
                model="nomic-embed-text",
                prompt=c["text"]
            )["embedding"]
            chunk_embeddings.append(np.array(emb))

        res = chunk.main_loop(chunk_embeddings, chunk.questions_rag, chunks)

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



