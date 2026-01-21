from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import chunk

app = FastAPI()

# Pour autoriser React à communiquer avec FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # autorise toutes les origines pour dev
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route POST pour recevoir un PDF
@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    # Affiche le nom du fichier reçu
    print(f"Nom du fichier reçu : {file.filename}")
    
    # Lire le contenu (optionnel)
    # content = await file.read()
    # print(f"Taille du fichier : {len(content)} bytes")
    
    # Ici tu pourrais appeler ta fonction Python sur le PDF
    text = chunk.pdfReader(file.filename)
    result = f"PDF '{file.filename}' reçu avec succès !"
    
    return {"message": result}


