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

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil
import chunk
import numpy as np
from sentence_transformers import CrossEncoder
import ollama

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    # 1️⃣ Sauvegarde temporaire
    file_path = f"/tmp/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2️⃣ Lecture PDF
    text = chunk.pdfReader(file_path)

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

    # 5️⃣ RAG
    res = chunk.main_loop(chunk_embeddings, chunk.QUESTION_RAG)

    # 6️⃣ Format React-friendly
    q_r = []
    for key, value in res.items():
        q_r.append({
            "question": key,
            "reponse": value
        })

    return q_r



