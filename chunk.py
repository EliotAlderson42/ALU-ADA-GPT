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
        "keyword": "Type"
    },
    {
        "llm": "Quelle est la nature de l’opération (construction neuve, extension, réhabilitation, rénovation, restructuration) ?",
        "rerank": "Nature du projet (neuf, extension, réhabilitation, rénovation, restructuration)",
        "keyword" : "Nature"
    },
    {
        "llm": "Quel est le montant prévisionnel des travaux indiqué dans le document ?",
        "rerank": "Montant/prix/cout prévisionnel du projet",
        "keyword" : "Travaux"
    },
    {
        "llm": "Dans quelle région administrative se situe le projet en te basant sur le texte fourni?",
        "rerank": "Région administrative du projet",
        "keyword": "Region"
    },
    {
        "llm": "Extrait le nom du département si celui-ci est écrit dans le texte fourni dans le cas contraire répond simplement: Non précisé",
        "rerank": "Quel est le département/code postal du projet",
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
        "rerank": "Commune ou ville du projet"
    },
    {
        "llm": "Quelle est la succursale ou l’agence territoriale la plus proche mentionnée dans le document ?",
        "keyword": "Succursale",
        "rerank": "Succursale ou agence territoriale la plus proche"
    },
    {
        "llm": "Qui est le maître d’ouvrage du projet tel qu’indiqué dans le document ?",
        "keyword": "Ouvrage",
        "rerank": "Maître d’ouvrage"
    },
    {
        "llm": "Quel est le type de sélection prévu (appel à candidatures ou appel d’offres) ?",
        "keyword": "Candidature",
        "rerank": "Type de sélection (appel à candidatures / appel d’offres)"
    },
    {
        "llm": "Quel est le type de procédure de passation du marché (appel d’offres, concours, marché global de performance, procédure adaptée, etc.) ?",
        "keyword": "Procédure",
        "rerank": "Type de procédure (AO, concours, MGP, etc.)"
    },
    {
        "llm": "Le document précise-t-il qu’un mandataire est requis ? Si oui, quel type de mandataire est demandé ?",
        "keyword": "Mandataire",
        "rerank": "Mandataire requis et type"
    },
    {
        "llm": "Quelle est la date limite de remise des candidatures ou des offres (première échéance) ?",
        "keyword": "limite1", ##
        "rerank": "Quelle est la date limite de remise des candidatures"
    },
    {
        "llm": "Quelle est la date limite pour poser des questions ou demander des précisions auprès du maître d’ouvrage ?",
        "keyword": "Questions",
        "rerank": "Date limite pour questions"
    },
    {
        "llm": "Quelle est la date limite de remise des offres ou des candidatures (seconde échéance), si elle est mentionnée ?",
        "keyword": "Limite2",
        "rerank": "Date de remise n°2"
    },
    {
        "llm": "Une exclusivité est-elle imposée aux bureaux d’études ? Si oui, sur combien d’équipes cette exclusivité s’applique-t-elle ?",
        "rerank": "Exclusivité bureaux d’études (oui/non) et nombre d’équipes",
        # "rerank": "Le document prévoit-il une exclusivité imposée pour les bureaux d’études ?",
        "keyword": "Exclusivité"
    },
    {
        # "llm": "Une visite du site est-elle prévue ? Si oui, à quelle date ?",
        # "rerank": "Y a t-il un rendez-vous sur site ?",
        # "keyword": "Visite"
        "llm": "Le document mentionne-t-il une visite, une réunion ou un déplacement sur site prévu pour les candidats ou les participants ? Si oui à quelle date ?",
        "rerank": "Présence sur site, réunion ou visite organisée dans le cadre du projet ou du concours ?",
        "keyword": "Présence sur site"
    },
    {
        "llm": "Quelles sont les compétences ou spécialités exigées pour la constitution de l’équipe candidate ?",
        "rerank": "Compétences ou spécialités requises pour l’équipe",
        "keyword": "Compétences"
    },
    {
        "llm": "Combien de références professionnelles minimum sont demandées à l’architecte dans le cadre de la candidature ?",
        "rerank": "Combien de références sont demandées à l’architecte?",
        "keyword": "Références"
    },
    {
        "llm": "Quelles sont les missions confiées au titulaire du marché (par exemple : mission complète, DIAG, FAISA, REL, EXE, etc.) ?",
        "rerank": "Missions demandées (mission complète, DIAG, FAISA, REL, EXE, etc.)",
        "keyword": "Missions"
    },
    {
        "llm": "Le marché est-il découpé en tranches ? Si oui, combien de tranches sont prévues et quelles sont leurs natures (tranche ferme, tranche optionnelle) ?",
        "rerank": "Le marché est-il découpé en tranches (nombre et type : ferme / optionnelle)",
        "keyword": "Tranches"
    },
    {
        "llm": "Quelles sont les phases de la mission, combien sont-elles et quelle est leur temporalité prévisionnelle ?",
        "rerank": "Phases de la mission (nombre et temporalité)",
        "keyword": "Phases"
    },
    {
        # "llm": "Le projet prévoit-il l’intervention d’une AMO ou d’un MOD ? Si oui, lequel et par qui est-il assuré ?",
        # "rerank": "AMO ou MOD et entité concernée"
        "llm": "Le projet prévoit-il l’intervention d’une assistance à maîtrise d’ouvrage ou d’un maître d’ouvrage délégué ? Si oui, lequel et quelle entité en est responsable ?",
        "rerank": "Assistance à maîtrise d’ouvrage ou maîtrise d’ouvrage déléguée et entité responsable",
        "keyword": "Assistances"
    },
    {
        "llm": "Une prime de concours est-elle prévue ? Si oui, quel est le montant de cette prime ?",
        # "rerank": "Prime de concours (oui/non) et montant",
        "rerank": "Remise ou versement de prime avec montant",
        "keyword": "Prime"
    },
    {
        "llm": "Le document impose-t-il la réalisation d’une maquette (numérique ou physique) dans le cadre de la candidature ou de l’offre ?",
        "rerank": "Maquette requise (oui/non)",
        "keyword": "Maquette"
    },
    {
        "llm": "La réalisation d’un film de présentation est-elle exigée dans le cadre de la procédure ?",
        "rerank": "Film requis (oui/non)",
        "keyword": "Film"
    },
    {
        "llm": "Quels sont les critères d’appréciation ou d’évaluation mentionnés dans le texte et quels sont leurs pourcentages respectifs ?",
        "rerank": "Critères d’appréciation ou d’évaluation d’une offre avec pondération ou pourcentage (prix, valeur technique, délais).",
        "keyword": "pourcentages"
    }
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

    while start < len(words):
        end = start + chunk_size
        chunk = words[start:end]
        # chunk = re.sub(rf"{re.escape('.')}+", '.', words[start:end])
        chunks.append(" ".join(chunk))
        start += chunk_size - overlap

    # print(chunks)
    return chunks
##################################################################################################
def travel_time(ville):
    # name = ville.split()
    # name = name[0] + ", France"

    geolocator = Nominatim(user_agent="my_geocoder")
    data = geolocator.geocode(ville + ", France")
    data1 = geolocator.geocode("Epinay-sur-Orge, France")
    url = f"http://router.project-osrm.org/route/v1/driving/{data1.longitude},{data1.latitude};{data.longitude},{data.latitude}?overview=false"
    res = requests.get(url).json()

    duree_sec = res['routes'][0]['duration']
    print(f"Temps de trajet pour se rendre à {ville}: {duree_sec/3600:.2f} heures")
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
def pdfReader():
    text = ""
    with pdfplumber.open("document.pdf") as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text
# print(f"La duree de l'extraction du pdf a duree {time.time() - start}")

start = time.time()
chunks = chunk_text(text)

# for chunk in chunks:
#     print(f"{chunk}\n")
##Transformation de chaque chunk en embeddings = transformation numerique
chunk_embeddings = []
for chunk in chunks:
    emb = ollama.embeddings(
        model="nomic-embed-text",
        prompt=chunk
    )["embedding"]
    chunk_embeddings.append(np.array(emb))

print(f"La creation des chunks + embeddings a durée {time.time() - start}")

reranker = CrossEncoder("BAAI/bge-reranker-large")

ollama_url = "http://localhost:11434/api/chat"

prompt_ville = """Tu es un extracteur strict.
Ta tâche est d’extraire UNE entité de type VILLE.

Règles ABSOLUES :
- La réponse doit contenir exactement un seul mot ou groupe de mots.
- Ce mot doit être UNIQUEMENT le nom de la ville (ex: "Lyon", "Saint-Denis").
- Il est INTERDIT d’inclure un code postal, un département, une région ou un pays.
- Il est INTERDIT d’ajouter des commentaires, phrases ou explications.
- Si aucune ville n’est clairement mentionnée, réponds exactement : Non précisé
- Ne donne aucun contexte."""

total = time.time()
data = {}
# for i in range(len(questions_rag)):
if True:
    start = time.time()
    question_emb = np.array(ollama.embeddings(model="nomic-embed-text", prompt=questions_rag[2]["rerank"])["embedding"])
    similarities = [cosine_similarity(question_emb, emb) for emb in chunk_embeddings]
    top10_chunk = np.argsort(similarities)[-10:][::-1]
    best_chunks = [chunks[i] for i in top10_chunk]
    reranked_chunks = rerank(questions_rag[2]["rerank"], best_chunks)
    top5real = reranked_chunks[:5]
    merged_context = "\n\n".join(f"EXTRAIT{i + 1}:\n{chunk}" for i, chunk in enumerate(top5real))
    # context = "\n\n".join(reranked_chunks[0][0])
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
{merged_context}

QUESTION:
{questions_rag[2]["llm"]}
"""
            }
        ],
        "stream": False
    }
    if questions_rag[2]["keyword"] == "Ville":
        playload["messages"][0]["content"] = prompt_ville
    response = requests.post(ollama_url, json=playload)
    response.raise_for_status()
    answer = response.json()["message"]["content"]
    print(questions_rag[2]["llm"])
    print("\n\n")
    # print(f"{merged_context}\n\n")
    # print("'''''''''''''''''''''''''''''")
    # print("-------------------------")
    print(answer)
    if questions_rag[2]["keyword"] == "Ville":
        print(f"EPCI de la ville/commune = {get_epci(answer)['nom']}")
        travel_time(answer)
    print(f"Question n°{2}/{len(questions_rag)} = {time.time() - start:.2f}secondes de temps de reponse")
    print("-------------------------")
    data[questions_rag[2]["keyword"]] = answer
    # print(len(chunks))

print(f"Toutes les questions = {(time.time() - total) / 60:.2f}minutes")
# travelTime(data["Ville"])