import fitz
import io
import pdfplumber
import numpy as np
import ollama
import re
import requests
import time
import unicodedata
import pysbd
# import metadata
from backend import prompt_list
from backend import add_metadata
from sentence_transformers import CrossEncoder
from sklearn.cluster import KMeans
from collections import defaultdict


##Fonction pour retrier plus pointilleusement les n meilleurs chunks 
def rerank(question, chunks):
    pairs = [(question, chunk) for chunk in chunks]
    scores = reranker.predict(pairs)

    ranked = sorted(zip(chunks, scores), key=lambda x: x[1], reverse=True)
    return ranked

##Fonction pour verifier si les deux vecteurs pointent dans la meme direction
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def nettoyer_caracteres_repetes(text):

    if not text or not isinstance(text, str):
        return text
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"\.+", ".", text)
    text = re.sub(r",+", ",", text)
    text = re.sub(r";+", ";", text)
    text = re.sub(r":+", ":", text)
    text = re.sub(r"-+", "-", text)
    text = re.sub(r"_+", "_", text)
    text = re.sub(r'"+', '"', text)
    text = re.sub(r"'+", "'", text)
    text = re.sub(r"\(+", "(", text)
    text = re.sub(r"\)+", ")", text)
    text = re.sub(r" *\n *", "\n", text)
    # print("SALUT 2")
    return text.strip()


##################################################################################################
# def travel_time(ville):
#     """
#     Calcule le temps de trajet vers une ville (optionnel, ne bloque pas si erreur).
#     """
#     try:
#         if not ville or ville.upper() in ["AUCUNE", "NON PRÉCISÉ", "INFORMATION NON PRÉCISÉ"]:
#             return  # Pas de calcul si pas de ville
        
#         geolocator = Nominatim(user_agent="my_geocoder")
#         data = geolocator.geocode(ville + ", France", timeout=10)
        
#         if not data:
#             print(f"Ville '{ville}' non trouvée pour le calcul de trajet")
#             return
        
#         data1 = geolocator.geocode("Epinay-sur-Orge, France", timeout=10)
#         if not data1:
#             print("Point de départ (Epinay-sur-Orge) non trouvé")
#             return
        
#         url = f"http://router.project-osrm.org/route/v1/driving/{data1.longitude},{data1.latitude};{data.longitude},{data.latitude}?overview=false"
#         res = requests.get(url, timeout=10)
#         res.raise_for_status()
#         route_data = res.json()
        
#         if 'routes' in route_data and len(route_data['routes']) > 0:
#             duree_sec = route_data['routes'][0]['duration']
#             print(f"Temps de trajet pour se rendre à {ville}: {duree_sec/3600:.2f} heures")
#         else:
#             print(f"Impossible de calculer le trajet vers {ville}")
#     except Exception as e:
#         # Ne pas faire planter le programme si le calcul de trajet échoue
#         print(f"Erreur lors du calcul du temps de trajet vers {ville}: {str(e)}")
#         pass
#################################################################################################
# def get_epci(ville):
#     url = f"https://geo.api.gouv.fr/communes?nom={ville}&fields=codeEpci,epci&limit=1"
#     reponse = requests.get(url)
#     data = reponse.json()

#     if not data:
#         return "Pas trouver"
#     commune = data[0]
#     epci = commune.get("epci")
#     return epci

# start = time.time()

def normalisation_pdf(file):
    doc = fitz.open(file)

    for page in doc:
        rect = page.rect
        # Coupe les 50 pixels en bas
        new_rect = fitz.Rect(rect.x0, rect.y0, rect.x1, rect.y1 - 200)
        page.set_cropbox(new_rect)

    output_buffer = io.BytesIO()
    doc.save(output_buffer)
    doc.close()
    return output_buffer.getvalue()



def pdfReader(file):
    text = ""
    with pdfplumber.open(io.BytesIO(normalisation_pdf(file))) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

# reranker = CrossEncoder("BAAI/bge-reranker-large")
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


OLLAMA_URL = "http://localhost:11434/api/chat"


def send_playload(questions_rag, context, i, prompt, max_retries=3, timeout=120):

    temperature = 1

    if questions_rag[i]["keyword"] == "Ville":
        prompt = prompt_list.VILLE
    elif questions_rag[i]["keyword"] == "Références":
        prompt = prompt_list.REFERENCE
        temperature = 0
    elif questions_rag[i]["keyword"] == "Méthodologie":
        prompt = prompt_list.NOTE

    playload = {
        "model": "gemma4:e4b",
        "stream": False, 
        "options": {
            "temperature": temperature,
            "top_p": 0.8,
            "num_ctx": 8192,
            "repeat_penalty": 1.1,
        },
        "messages": [
            {
                "role": "system",
                "content": prompt
            },
            {
                "role": "user",
                "content": f"""
CONTEXTE:
{context}

QUESTION:
{questions_rag[i]["llm"]}
"""
            }
        ],
    }
    last_error = None
    for attempt in range(max_retries):
        try:
            response = requests.post(
                OLLAMA_URL, 
                json=playload,
                timeout=timeout  # Timeout pour éviter les blocages
            )
            response.raise_for_status()
            
            # Vérifier que la réponse est valide
            result = response.json()
            if "message" not in result or "content" not in result["message"]:
                raise ValueError(f"Réponse Ollama invalide: {result}")
            
            return result["message"]["content"]
            
        except requests.exceptions.Timeout:
            last_error = f"Timeout après {timeout}s (tentative {attempt + 1}/{max_retries})"
            if attempt < max_retries - 1:
                time.sleep(2)  # Attendre 2s avant de réessayer
                continue
            else:
                raise Exception(f"Timeout Ollama après {max_retries} tentatives: {last_error}")
                
        except requests.exceptions.ConnectionError:
            last_error = f"Impossible de se connecter à Ollama à {OLLAMA_URL} (tentative {attempt + 1}/{max_retries})"
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            else:
                raise Exception(f"Ollama n'est pas accessible: {last_error}. Assure-toi qu'Ollama est démarré (ollama serve)")
                
        except requests.exceptions.HTTPError as e:
            error_msg = f"Erreur HTTP {e.response.status_code}"
            try:
                error_detail = e.response.json()
                if "error" in error_detail:
                    error_msg += f": {error_detail['error']}"
            except:
                error_msg += f": {e.response.text[:200]}"
            
            # Si erreur 404, le modèle n'existe peut-être pas
            if e.response.status_code == 404:
                raise Exception(f"Modèle 'mistral:7b-instruct' introuvable. Vérifie qu'il est installé: ollama pull mistral:7b-instruct")
            
            last_error = error_msg
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            else:
                raise Exception(f"Erreur HTTP Ollama après {max_retries} tentatives: {last_error}")
                
        except Exception as e:
            last_error = str(e)
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            else:
                raise Exception(f"Erreur lors de l'appel à Ollama après {max_retries} tentatives: {last_error}")
    
    # Ne devrait jamais arriver ici, mais au cas où
    raise Exception(f"Échec après {max_retries} tentatives: {last_error}")


def send_single_question(question, context, prompt=None, max_retries=3, timeout=120):
    """Envoie une seule question au LLM avec le contexte donné (pour question supplémentaire)."""
    if prompt is None:
        prompt = prompt_list.SYSTEM
    payload = {
        "model": "mistral:7b-instruct",
        "messages": [
            {"role": "system", "content": prompt},
            {
                "role": "user",
                "content": f"""CONTEXTE:
{context}

QUESTION:
{question}
""",
            },
        ],
        "stream": False,
        "options": {"temperature": 1, "top_p": 0.8, "num_ctx": 8192, "repeat_penalty": 1.1},
    }
    last_error = None
    for attempt in range(max_retries):
        try:
            response = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
            response.raise_for_status()
            result = response.json()
            if "message" not in result or "content" not in result["message"]:
                raise ValueError(f"Réponse Ollama invalide: {result}")
            return result["message"]["content"]
        except requests.exceptions.Timeout:
            last_error = f"Timeout après {timeout}s (tentative {attempt + 1}/{max_retries})"
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            raise Exception(f"Timeout Ollama après {max_retries} tentatives: {last_error}")
        except requests.exceptions.ConnectionError:
            last_error = f"Impossible de se connecter à Ollama (tentative {attempt + 1}/{max_retries})"
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            raise Exception(f"Ollama n'est pas accessible: {last_error}")
        except Exception as e:
            last_error = str(e)
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            raise
    raise Exception(f"Échec après {max_retries} tentatives: {last_error}")


def ask_supplementary_question(question, embeddings, chunks):
    """
    Pose une question supplémentaire sur le PDF : recherche sémantique sur tous les chunks,
    rerank, puis envoi au LLM. Utilisé par la page Réponses.
    """
    metadata.addMetaData(chunks, None)
    # Utiliser un keyword inconnu pour récupérer tous les chunks (branche else de match_metadata)
    data_embed, candidats = match_metadata("_supplement_", chunks, embeddings)
    if not candidats:
        return "Aucun extrait disponible pour répondre."
    question_emb = np.array(ollama.embeddings(model="nomic-embed-text", prompt=question)["embedding"])
    similarities = [cosine_similarity(question_emb, emb) for emb in data_embed]
    top_10 = np.argsort(similarities)[-10:][::-1]
    best_chunks = [candidats[idx]["text"] for idx in top_10]
    reranked = rerank(question, best_chunks)[:3]
    chunk_texts = [c for c, _ in reranked]
    merged_context = "\n\n".join(f"EXTRAIT{j + 1}:\n{t}" for j, t in enumerate(chunk_texts))
    return send_single_question(question, merged_context)


def add_question(question, keyword, rerank_query, embeddings, chunks):
    question_emb = np.array(ollama.embeddings(model="nomic-embed-text", prompt=rerank_query)["embedding"])
    add_metadata.addMetaData(chunks, None)
    data_embed, candidats = add_metadata.match_metadata(keyword, chunks, embeddings)

    if not candidats:
        return "Aucun extrait trouvé pour ce mot-clé."
        
    similarities = [cosine_similarity(question_emb, emb) for emb in data_embed]
    top_10 = np.argsort(similarities)[-10:][::-1]
    best_chunks = [candidats[idx]["text"] for idx in top_10]
    reranked = rerank(rerank_query, best_chunks)[:3]
    chunk_texts = [c for c, _ in reranked]
    merged_context = "\n\n".join(f"EXTRAIT{j + 1}:\n{t}" for j, t in enumerate(chunk_texts))
    print(f"QUESTION = {question}\n\nmerged_context = {merged_context}", flush=True)
    answer = send_single_question(question, merged_context)
    return answer
    
def main_loop(embeddings, questions_rag, chunks):
    q_r = {}
    data = [()]
    epci = str()

    header = "HEADER: \n" + chunks[0]["text"] + "\n\n" + chunks[1]["text"]
    prompt = prompt_list.SYSTEM
    add_metadata.addMetaData(chunks, None)
    # for chunk in chunks:
    #     print(f"TAILLE DU CHUNK = {len(chunk['text'])}; ID DU CHUNK == {chunk["metadata"]["id"]}")
    # return 0
    for i in range(len(prompt_list.questions_rag)):
            if i == 30: 
                print(f"KEYWORD = {prompt_list.questions_rag[i]['keyword']}")

                question_emb = np.array(ollama.embeddings(model="nomic-embed-text", prompt=prompt_list.questions_rag[i]["rerank"])["embedding"])
                data_embed, candidats = add_metadata.match_metadata(prompt_list.questions_rag[i]["keyword"], chunks, embeddings)
                print(f"TAILLE CANDIDATS = {len(candidats)}")
                for c in candidats:
                    print(f"ID == {c['metadata']['id']}")
                    print(f"TEXT == {c['text']}")
                    print("--------------------------------")
                similarities = [cosine_similarity(question_emb, emb) for emb in data_embed]
                top_10 = np.argsort(similarities)[-10:][::-1]        
                best_chunks = []

                for idx in top_10:
                    best_chunks.append(candidats[idx]["text"])

                reranked_chunks = rerank(prompt_list.questions_rag[i]["rerank"], best_chunks)[:2]
                merged_context = "\n\n".join(f"EXTRAIT{j + 1}:\n{chunk[0]}" for j, chunk in enumerate(reranked_chunks))
                if prompt_list.questions_rag[i]["keyword"] == "Mandataire" or prompt_list.questions_rag[i]["keyword"] == "Type":
                    merged_context += "\n\n" + header
                elif prompt_list.questions_rag[i]["keyword"] == "json":
                    merged_context = answer

                print(f"QUESTION = {prompt_list.questions_rag[i]['llm']}\n\nmerged_context = {merged_context}", flush=True)
                print(f"Questions n° {i + 1}/{len(prompt_list.questions_rag)}")

                answer = send_playload(prompt_list.questions_rag, merged_context, i, prompt)

                if prompt_list.questions_rag[i]["keyword"] == "Mandataire":
                    data.append(("acheteurId", answer))

                elif prompt_list.questions_rag[i]["keyword"] == "Type d'opération":
                    data.append(("operationType", answer))
                                
                q_r[prompt_list.questions_rag[i]["user"]] = answer
    
    return q_r, data
