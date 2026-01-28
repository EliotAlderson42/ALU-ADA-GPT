import pdfplumber
import numpy as np
import ollama
import re
import requests
import time
from sentence_transformers import CrossEncoder
from geopy.geocoders import Nominatim


questions_rag = [
    {
        "llm": "Quel est le type d'infrastructure décrit dans le document (exemple : école, gymnase, équipement culturel, bâtiment administratif) ?",
        "rerank": "Type de projet (école, gymnase, équipement culturel, bâtiment administratif)",
        "user": "Quel est le type d'infrastructure ?",
        "keyword": "Type"
    },
    {
        "llm": "Quelle est la nature de l’opération (construction neuve, extension, réhabilitation, rénovation, restructuration) ?",
        "rerank": "Nature du projet (neuf, extension, réhabilitation, rénovation, restructuration)",
        "user": "Quel est la nature de l'opération ?",
        "keyword" : "Nature"
    },
    {
        "llm": "Quel est le montant prévisionnel des travaux indiqué dans le document ?",
        "rerank": "Montant/prix/cout prévisionnel du projet",
        "user": "Quel est le montant prévisionnel des travaux ?",
        "keyword" : "Travaux"
    },
    {
        "llm": "Dans quelle région administrative se situe le projet en te basant sur le texte fourni?",
        "rerank": "Région administrative du projet",
        "user": "Dans quelle région administratif se situe le projet ?",
        "keyword": "Region"
    },
    {
        "llm": "Extrait le nom du département si celui-ci est écrit dans le texte fourni dans le cas contraire répond simplement: Non précisé",
        "rerank": "Dans quel code postal se trouve le projet",
        "user": "Dans quel département se situe le projet ?",
        "keyword": "Département"
    },
    # {
    #    "llm": "Quel est l’intercommunalité concerné par le projet et quel est son type (communauté de communes, communauté d’agglomération, métropole, etc.) ?",
    #    "keyword": "Intercommunalité",
    #    "rerank": "Intercommunalité concerné et type (communauté de communes, agglomération, métropole)"
    # },
    {
        "llm": "Extrait uniquement le nom de la ville mentionnée dans le texte ci-dessous. Réponds uniquement par le nom de la ville, sans phrase, sans ponctuation, sans explication.S’il n’y a pas de ville clairement identifiable, réponds exactement par : AUCUNE.",
        "keyword": "Ville",
        "user": "Quelle est le nom de la ville ou se situe le projet?",
        "rerank": "Commune ou ville du projet"
    },
    {
        "llm": "Quelle est la succursale ou l’agence territoriale la plus proche mentionnée dans le document ?",
        "keyword": "Succursale",
        "user": "Quelle est la succursale ou l'agence territoriale la plus proche ?",
        "rerank": "Succursale ou agence territoriale la plus proche"
    },
    {
        "llm": "Qui est le maître d’ouvrage du projet tel qu’indiqué dans le document ?",
        "keyword": "Ouvrage",
        "user": "Qui est le maitre d'ouvrages?",
        "rerank": "Maître d’ouvrage"
    },
    {
        "llm": "Quel est le type de sélection prévu (appel à candidatures ou appel d’offres) ?",
        "keyword": "Candidature",
        "user": "Quel est le type de sélection prévue?",
        "rerank": "Type de sélection (appel à candidatures / appel d’offres)"
    },
    {
        "llm": "Quel est le type de procédure de passation du marché (appel d’offres, concours, marché global de performance, procédure adaptée, etc.) ?",
        "keyword": "Procédure",
        "user": "Quel est le type de procédure de passation du marché ?",
        "rerank": "Type de procédure (AO, concours, MGP, etc.)"
    },
    {
        "llm": "Le document précise-t-il qu’un mandataire est requis ? Si oui, quel type de mandataire est demandé ?",
        "keyword": "Mandataire",
        "user": "Qui est le mandataire requis et quel est son type si il y en a un",
        "rerank": "Mandataire requis et type"
    },
    {
        "llm": "Quelle est la date limite de remise des candidatures ou des offres (première échéance) ?",
        "keyword": "limite1", ##
        "user": "Quelle est la date limite de remise des candidatures ?",
        "rerank": "Quelle est la date limite de remise des candidatures"
    },
    {
        "llm": "Quelle est la date limite pour poser des questions ou demander des précisions auprès du maître d’ouvrage ?",
        "keyword": "Questions",
        "user": "Quelle est la date limite pour demander des renseignements supplémentaires?",
        "rerank": "Date limite pour questions"
    },
    {
        "llm": "Quelle est la date limite de remise des offres ou des candidatures (seconde échéance), si elle est mentionnée ?",
        "user": "Quelle est la data limite de remises des candidatures (seconde échéance)?",
        "keyword": "Limite2",
        "rerank": "Date de remise n°2"
    },
    {
        "llm": "Une exclusivité est-elle imposée aux bureaux d’études ? Si oui, sur combien d’équipes cette exclusivité s’applique-t-elle ?",
        "rerank": "Exclusivité bureaux d’études (oui/non) et nombre d’équipes",
        "user" : "Y a t il une exclusivité sur les bureaux d'études et sur combien d'équipes ?",
        # "rerank": "Le document prévoit-il une exclusivité imposée pour les bureaux d’études ?",
        "keyword": "Exclusivité"
    },
    {
        # "llm": "Une visite du site est-elle prévue ? Si oui, à quelle date ?",
        # "rerank": "Y a t-il un rendez-vous sur site ?",
        # "keyword": "Visite"
        "llm": "Le document mentionne-t-il une visite, une réunion ou un déplacement sur site prévu pour les candidats ou les participants ? Si oui à quelle date ?",
        "rerank": "Présence sur site, réunion ou visite organisée dans le cadre du projet ou du concours ?",
        "user" : "Est-ce qu'une visite du site est obligatoire?",
        "keyword": "Présence sur site"
    },
    {
        "llm": "Quelles sont les compétences ou spécialités exigées pour la constitution de l’équipe candidate ?",
        "rerank": "Compétences ou spécialités requises pour l’équipe",
        "user": "Quelles sont les compétences exigées pour la constitution de l'équipe ?",
        "keyword": "Compétences"
    },
    {
        "llm": "Combien de références professionnelles minimum sont demandées à l’architecte dans le cadre de la candidature ?",
        "rerank": "Combien de références sont demandées à l’architecte?",
        "user": "Combien de références minimum sont demandées a l'architecte?",
        "keyword": "Références"
    },
    {
        "llm": "Quelles sont les missions confiées au titulaire du marché (par exemple : mission complète, DIAG, FAISA, REL, EXE, etc.) ?",
        "rerank": "Missions demandées (mission complète, DIAG, FAISA, REL, EXE, etc.)",
        "user": "Quelles sont les missions demandées au titulaire du marché",
        "keyword": "Missions"
    },
    {
        "llm": "Le marché est-il découpé en tranches ? Si oui, combien de tranches sont prévues et quelles sont leurs natures (tranche ferme, tranche optionnelle) ?",
        "rerank": "Le marché est-il découpé en tranches (nombre et type : ferme / optionnelle)",
        "user": "Le marché est-il découpé en tranches? Si oui, lesquelles?",
        "keyword": "Tranches"
    },
    {
        "llm": "Quelles sont les phases de la mission, combien sont-elles et quelle est leur temporalité prévisionnelle ?",
        "rerank": "Phases de la mission (nombre et temporalité)",
        "user": "Quelles sont les phases de la mission?",
        "keyword": "Phases"
    },
    {
        # "llm": "Le projet prévoit-il l’intervention d’une AMO ou d’un MOD ? Si oui, lequel et par qui est-il assuré ?",
        # "rerank": "AMO ou MOD et entité concernée"
        "llm": "Le projet prévoit-il l’intervention d’une assistance à maîtrise d’ouvrage ou d’un maître d’ouvrage délégué ? Si oui, lequel et quelle entité en est responsable ?",
        "rerank": "Assistance à maîtrise d’ouvrage ou maîtrise d’ouvrage déléguée et entité responsable",
        "user": "Le projet prévoit il l'intervention d'une assistance a maitrise d'ouvrages?",
        "keyword": "Assistances"
    },
    {
        "llm": "Une prime de concours est-elle prévue ? Si oui, quel est le montant de cette prime ?",
        # "rerank": "Prime de concours (oui/non) et montant",
        "rerank": "Remise ou versement de prime avec montant",
        "user": "Une prime de concours est-elle prévue? Si oui, quel est son montant?",
        "keyword": "Prime"
    },
    {
        "llm": "Le document impose-t-il la réalisation d’une maquette (numérique ou physique) dans le cadre de la candidature ou de l’offre ?",
        "rerank": "Maquette requise (oui/non)",
        "user": "La réalisation d'une maquette est elle imposé?",
        "keyword": "Maquette"
    },
    {
        "llm": "La réalisation d’un film de présentation est-elle exigée dans le cadre de la procédure ?",
        "rerank": "Film requis (oui/non)",
        "user": "La réalisation d'un film est-elle imposée?",
        "keyword": "Film"
    },
    # {
    #     "llm": "Quels sont les critères d’appréciation ou d’évaluation mentionnés dans le texte et quels sont leurs pourcentages respectifs ?",
    #     "rerank": "Critères d’appréciation ou d’évaluation d’une offre avec pondération ou pourcentage (prix, valeur technique, délais).",
    #     "keyword": "pourcentages"
    # }
]

system_prompt = """
Tu es un assistant spécialisé dans l'analyse d'appels d'offres et de marché public;
Tu extrais uniquement des informations factuelles présentes dans le contexte fourni.

Règles:
-N'invente jamais.
-Si l'information n'est pas renseigné dans le texte fourni répond juste: "Information non précisé"

Format:
-Réponse courte et factuelle.
-Pas d'éxplication.
"""

##Fonction pour retrier plus pointilleusement les n meilleurs chunks 
def rerank(question, chunks):
    pairs = [(question, chunk) for chunk in chunks]
    scores = reranker.predict(pairs)

    ranked = sorted(zip(chunks, scores), key=lambda x: x[1], reverse=True)
    return ranked

##Fonction pour verifier si les deux vecteurs pointent dans la meme direction
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

##Fonction pour decouper mon pdf en plusieurs petits bouts lisible pour eviter de trop consommer
def chunk_text(text, chunk_size=300, overlap=50):
    words = text.split()
    chunks = []
    start = 0
    i = 0

    while start < len(words):
        end = start + chunk_size

        chunk_text_str = " ".join(words[start:end])

        chunk = {
            "text": chunk_text_str,
            "metadata": {
                "id": i,
                "has_postal_code": False,
                "has_price": False,
                "has_date": False,
                "language": "fr",
            },
            "llm_hints": [],
        }

        chunks.append(chunk)

        start += chunk_size - overlap
        i += 1

    return chunks

# def chunk_text(text, chunk_size=300, overlap=50):
#     words = text.split()
#     chunks = []
#     start = 0
#     i = 0
#     while start < len(words):
#         chunk = {
#             "text": "",
#             "metadata": {
#                 "id": i,
#                 "has_postal_code": False,
#                 "has_price": False,
#                 "has_date": False,
#                 "language": "fr",
#             },
#             "llm_hints": "",
#         }
#         end = start + chunk_size
#         chunk["text"] = words[start:end]
#         # chunk = re.sub(rf"{re.escape('.')}+", '.', words[start:end])
#         chunks.append(" ".join(chunk))
#         start += chunk_size - overlap
#         i += 1
#     # print(chunks)
#     return chunks

##################################################################################################
def travel_time(ville):
    """
    Calcule le temps de trajet vers une ville (optionnel, ne bloque pas si erreur).
    """
    try:
        if not ville or ville.upper() in ["AUCUNE", "NON PRÉCISÉ", "INFORMATION NON PRÉCISÉ"]:
            return  # Pas de calcul si pas de ville
        
        geolocator = Nominatim(user_agent="my_geocoder")
        data = geolocator.geocode(ville + ", France", timeout=10)
        
        if not data:
            print(f"Ville '{ville}' non trouvée pour le calcul de trajet")
            return
        
        data1 = geolocator.geocode("Epinay-sur-Orge, France", timeout=10)
        if not data1:
            print("Point de départ (Epinay-sur-Orge) non trouvé")
            return
        
        url = f"http://router.project-osrm.org/route/v1/driving/{data1.longitude},{data1.latitude};{data.longitude},{data.latitude}?overview=false"
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        route_data = res.json()
        
        if 'routes' in route_data and len(route_data['routes']) > 0:
            duree_sec = route_data['routes'][0]['duration']
            print(f"Temps de trajet pour se rendre à {ville}: {duree_sec/3600:.2f} heures")
        else:
            print(f"Impossible de calculer le trajet vers {ville}")
    except Exception as e:
        # Ne pas faire planter le programme si le calcul de trajet échoue
        print(f"Erreur lors du calcul du temps de trajet vers {ville}: {str(e)}")
        pass
#################################################################################################
def get_epci(ville):
    url = f"https://geo.api.gouv.fr/communes?nom={ville}&fields=codeEpci,epci&limit=1"
    reponse = requests.get(url)
    data = reponse.json()

    if not data:
        return "Pas trouver"
    commune = data[0]
    epci = commune.get("epci")
    return epci

start = time.time()
##Lecture du pdf into chunk
# def pdfReader():
#     text = ""
#     with pdfplumber.open("document.pdf") as pdf:
#         for page in pdf.pages:
#             page_text = page.extract_text()
#             if page_text:
#                 text += page_text + "\n"
#     return text

def pdfReader(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def addMetaData(chunk):
    mois = "janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre"
    pattern = r"\d{5}"
    if re.search(r"\d{5}", chunk):
        chunk["metadata"]["has_code_postale"] = True
    pattern = r"\b\d{1,3}(?:[ .]?\d{3})*(?:[.,]\d{1,2})?\s?[€$]?\b"
    if re.search(pattern, chunk):
        chunk["metadata"]["has_price"] = True
    pattern = r"\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b"
    pattern2 = rf"\b\d{{1,2}}\s(?:{mois})\s\d{{4}}\b"
    if re.search(pattern, chunk) or re.search(pattern2, chunk):
        chunk["metadata"]["has_date"] = True
    


reranker = CrossEncoder("BAAI/bge-reranker-large")

OLLAMA_URL = "http://localhost:11434/api/chat"

def check_ollama_health():
    """Vérifie que Ollama est accessible et que le modèle existe."""
    try:
        # Vérifier que le serveur Ollama répond
        health_url = "http://localhost:11434/api/tags"
        response = requests.get(health_url, timeout=5)
        response.raise_for_status()
        
        # Vérifier que le modèle existe
        models = response.json().get("models", [])
        model_names = [m.get("name", "") for m in models]
        required_model = "mistral:7b-instruct"
        
        if required_model not in model_names:
            available = ", ".join(model_names[:5]) if model_names else "aucun"
            raise Exception(
                f"Modèle '{required_model}' non trouvé. "
                f"Modèles disponibles: {available}. "
                f"Installe-le avec: ollama pull {required_model}"
            )
        
        return True
    except requests.exceptions.ConnectionError:
        raise Exception(
            "Ollama n'est pas accessible à http://localhost:11434. "
            "Assure-toi qu'Ollama est démarré: ollama serve"
        )
    except Exception as e:
        raise Exception(f"Erreur lors de la vérification d'Ollama: {str(e)}")

prompt_ville = """Tu es un extracteur strict.
Ta tâche est d’extraire UNE entité de type VILLE.

Règles ABSOLUES :
- La réponse doit contenir exactement un seul mot ou groupe de mots.
- Ce mot doit être UNIQUEMENT le nom de la ville (ex: "Lyon", "Saint-Denis").
- Il est INTERDIT d’inclure un code postal, un département, une région ou un pays.
- Il est INTERDIT d’ajouter des commentaires, phrases ou explications.
- Si aucune ville n’est clairement mentionnée, réponds exactement : Non précisé
- Ne donne aucun contexte."""

def send_playload(questions_rag, context, i, max_retries=3, timeout=120):

    playload = {
        "model": "mistral:7b-instruct",
        "messages": [
            {
                "role": "system",
                "content": system_prompt
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
        "stream": False       
    }
    if questions_rag[i]["keyword"] == "Ville":
        playload["messages"][0]["content"] = prompt_ville
    
    # Limiter la taille du contexte pour éviter les timeouts
    max_context_length = 8000  # caractères max
    if len(playload["messages"][1]["content"]) > max_context_length:
        # Tronquer le contexte si trop long
        truncated_context = context[:max_context_length - 500] + "\n\n[... contexte tronqué ...]"
        playload["messages"][1]["content"] = f"""
CONTEXTE:
{truncated_context}

QUESTION:
{questions_rag[i]["llm"]}
"""
    
    # Retry logic
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

def match_metadata(keyword, chunks):
    candidats = []
    if keyword == "limite1" or keyword == "limite2" or keyword == "questions":
        candidats = [chunk for chunks in chunks if chunk["metadata"]["has_date"]]
    elif keyword == "Travaux":
        candidats = [chunk for chunks in chunks if chunk["metadata"]["has_price"]]
    elif keyword == "département":
        candidats = [chunk for chunks in chunks if chunk["metadata"]["has_postal_code"]]
    return candidats


def main_loop(embeddings, questions_rag, chunks):
    q_r = {}
    for i in range(len(questions_rag)):
        question_emb = np.array(ollama.embeddings(model="nomic-embed-text", prompt=questions_rag[i]["rerank"])["embedding"])

        # Correction: utiliser 'embeddings' au lieu de 'chunk_embeddings'
        similarities = [cosine_similarity(question_emb, emb) for emb in embeddings]
        top_10 = np.argsort(similarities)[-10:][::-1]
        # Correction: utiliser 'idx' au lieu de 'i' pour éviter la collision de variables
        print(chunks[3]["text"])
        best_chunks = []
        for idx in top_10:
            best_chunks.append(chunks[idx]["text"])
        print("SALUT")
        
        # Correction: passer la question textuelle au rerank, pas l'embedding
        reranked_chunks = rerank(questions_rag[i]["rerank"], best_chunks)[:5]
        
        # Correction: inclure le texte des chunks dans le contexte
        merged_context = "\n\n".join(f"EXTRAIT{j + 1}:\n{chunk[0]}" for j, chunk in enumerate(reranked_chunks))
        
        answer = send_playload(questions_rag, merged_context, i)

        if questions_rag[i]["keyword"] == "Ville":
            travel_time(answer)
        
        # Correction: déplacer cette ligne DANS la boucle
        q_r[questions_rag[i]["user"]] = answer
    
    return q_r

    # print(len(chunks))


total = time.time()
data = {}
# for i in range(len(questions_rag)):
# if True:
#     start = time.time()
#     question_emb = np.array(ollama.embeddings(model="nomic-embed-text", prompt=questions_rag[2]["rerank"])["embedding"])
#     similarities = [cosine_similarity(question_emb, emb) for emb in chunk_embeddings]
#     top10_chunk = np.argsort(similarities)[-10:][::-1]
#     best_chunks = [chunks[i] for i in top10_chunk]
#     reranked_chunks = rerank(questions_rag[2]["rerank"], best_chunks)
#     top5real = reranked_chunks[:5]
#     merged_context = "\n\n".join(f"EXTRAIT{i + 1}:\n{chunk}" for i, chunk in enumerate(top5real))
#     # context = "\n\n".join(reranked_chunks[0][0])
#     playload = {
#      "model": "mistral:7b-instruct",
#         "messages": [
#             {
#                 "role": "system",
#                 "content": system_prompt
#             },
#             {
#                 "role": "user",
#                 "content": f"""
# CONTEXTE:
# {merged_context}

# QUESTION:
# {questions_rag[2]["llm"]}
# """
#             }
#         ],
#         "stream": False
#     }
#     if questions_rag[2]["keyword"] == "Ville":
#         playload["messages"][0]["content"] = prompt_ville
#     response = requests.post(ollama_url, json=playload)
#     response.raise_for_status()
#     answer = response.json()["message"]["content"]
#     print(questions_rag[2]["llm"])
#     print("\n\n")
#     # print(f"{merged_context}\n\n")
#     # print("'''''''''''''''''''''''''''''")
#     # print("-------------------------")
#     print(answer)
#     if questions_rag[2]["keyword"] == "Ville":
#         print(f"EPCI de la ville/commune = {get_epci(answer)['nom']}")
#         travel_time(answer)
#     print(f"Question n°{2}/{len(questions_rag)} = {time.time() - start:.2f}secondes de temps de reponse")
#     print("-------------------------")
#     data[questions_rag[2]["keyword"]] = answer
#     # print(len(chunks))

# print(f"Toutes les questions = {(time.time() - total) / 60:.2f}minutes")
# # travelTime(data["Ville"])