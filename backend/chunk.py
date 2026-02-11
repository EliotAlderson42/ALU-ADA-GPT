import pdfplumber
import numpy as np
import ollama
import re
import requests
import time
import pysbd
from backend import add_metadata
from sentence_transformers import CrossEncoder
from sklearn.cluster import KMeans
from collections import defaultdict


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
        # "llm": "Donne moi le montant prévisionnel des travaux/projet indiqué dans le document ? Ou n'importe quel montant proposer par le document en echange de services. Explique a quoi sert le prix donner",
        "llm": "Analyse le document et indique le montant financier associé au projet (estimation, plafond, budget ou valeur du marché). Si plusieurs montants apparaissent, mentionne-les. Pour chaque montant, explique ce qu’il représente (limite maximale, coût prévu, montant contractuel, etc.) et à quoi il sert dans la consultation.",
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
        "llm": "Extrait le(s) code(s) postal ou le(s) département(s) dans lequel se situe le projet",
        "rerank": "Dans quel code postal/département se trouve le projet",
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
        "llm": "Qui est le maître d'ouvrage et quelles sont les informations que tu peux en extraire ? Si tu n'en as aucune répond juste avec le nom de maitre d'ouvrage",
        "keyword": "Ouvrage",
        "user": "Qui est le maitre d'ouvrages?",
        "rerank": "Maître d’ouvrage"
    },
    {
        "llm": "Qui est le mandataire si il y en un? Extraits le numérode telephone, l'adresse, l'adresse mail, le site web et le nom du mandataire dans ce format'Nom de la commune avec EPCI si possible - Tél: numero de telephone - Représentant de l'acheteur: Nom du representant si il yen a un, site de l'acheteur: site - Adresse mail de l'acheteur: mail' et n'ajoute rien d'autres que ces infos",
        "keyword": "Mandataire",
        "user": "Qui est le mandataire du projet si il y en a un?",
        "rerank": "Mandataire du projet agissant pour le compte du maître d'ouvrage"
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
        "keyword": "Mandataire-requis",
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
        "keyword": "Seconde échéance",
        "rerank": "Seconde échéance date limite de remise des candidatures"
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
    {
        "llm": "Un numéro de consultation se trouve probablment dans les extraits fournis. Extrais ce qui te semble être le numéro de consultation si rien n'y correspond répond 'Information non précisé'",
        "rerank": "Numéro de consultation ou d'appel d'offres",
        "user": "Quel est le numéro de consultation ou d'appel d'offres?",
        "keyword": "Numéro"
    },
    {
        "llm": "Quel est le type d'opération, sur quelle infrastructure et ou se situe l'infrastruscture en question ? Si tu ne trouves pas la réponses dans les ectraits fournis répond 'Non précisé'",
        "rerank": "Type d'opération et infrastructure",
        "user": "Quel est le type d'opération et sur quelle infrastructure ?",
        "keyword": "Type d'opération"
    },
    # {
    #     "llm": "Quels sont les critères d’appréciation ou d’évaluation mentionnés dans le texte et quels sont leurs pourcentages respectifs ?",
    #     "rerank": "Critères d’appréciation ou d’évaluation d’une offre avec pondération ou pourcentage (prix, valeur technique, délais).",
    #     "keyword": "pourcentages"
    # }
]

prompt_ville = """
Tu es un extracteur strict.
Ta tâche est d’extraire UNE entité de type VILLE.

Règles ABSOLUES :
- La réponse doit contenir exactement un seul mot ou groupe de mots.
- Ce mot doit être UNIQUEMENT le nom de la ville (ex: "Lyon", "Saint-Denis").
- Il est INTERDIT d’inclure un code postal, un département, une région ou un pays.
- Il est INTERDIT d’ajouter des commentaires, phrases ou explications.
- Si aucune ville n’est clairement mentionnée, réponds exactement : Non précisé
- Ne donne aucun contexte."""

system_prompt = """
Tu es un assistant spécialisé dans l'analyse d'appels d'offres et de marché public;
Tu extrais uniquement des informations factuelles présentes dans le contexte fourni.

Règles:
-N'invente jamais.
-Si il y a plusieurs questions, réponds uniquement à celles dont la réponses est fourni dans le texte fournis et ignore les autres.
-Si l'information n'est pas renseigné dans le texte fourni répond juste: "Information non précisé"

Format:
-Réponse courte et factuelle.
-Pas d'éxplication.
-Ne formule pas de phrases.
-Répond uniquement par la réponse attendu. 
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
                "has_offer_type": False,
                "has_nature_operation": False,
                "has_master_work": False,
                "has_mandataire_requis": False,
                "has_exclusivity": False,
                "has_visite": False,
                "has_competences": False,
                "has_missions": False,
                "has_maquette": False,
                "has_film": False,
                "has_références": False,
                "has_tranches": False,
                "has_second_deadline": False,
                "has_number": False,
                "has_operation_type": False,
                # "has_intervention": False,
            },
        }

        chunks.append(chunk)

        start += chunk_size - overlap
        i += 1

    return chunks


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

def pdfReader(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return nettoyer_caracteres_repetes(text)

def addMetaData(chunks):
    for chunk in chunks:
        add_metadata.add_price_metadata(chunk)
        add_metadata.add_date_metadata(chunk)
        add_metadata.add_postal_code_metadata(chunk)
        add_metadata.add_offer_type_metadata(chunk)
        add_metadata.add_nature_operation_metadata(chunk)
        add_metadata.add_master_work_metadata(chunk)
        add_metadata.add_mandataire_metadata(chunk)
        add_metadata.add_exclusivity_metadata(chunk)
        add_metadata.add_visite_metadata(chunk)
        add_metadata.add_competences_metadata(chunk)
        add_metadata.add_missions_metadata(chunk)
        add_metadata.add_maquette_metadata(chunk)
        add_metadata.add_film_metadata(chunk)
        add_metadata.add_references_metadata(chunk)
        add_metadata.add_tranches_metadata(chunk)
        add_metadata.add_second_deadline_metadata(chunk)
        add_metadata.add_number_metadata(chunk)
        add_metadata.add_operation_type_metadata(chunk)
        # add_metadata.add_intervention_metadata(chunk)   
        # return chunks

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
    # max_context_length = 8000  # caractères max
    # if len(playload["messages"][1]["content"]) > max_context_length:
        # Tronquer le contexte si trop long
        # truncated_context = context[:max_context_length - 500] + "\n\n[... contexte tronqué ...]"
    playload["messages"][1]["content"] = f"""
CONTEXTE:
{context}

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

def match_metadata(keyword, chunks, embeddings):
    candidats = []
    candidats_emb = []
    addMetaData(chunks)
    if keyword in ("limite1", "Limite2", "limite2", "questions"):
        candidats = [chunk for chunk in chunks if chunk["metadata"]["has_date"]]
    elif keyword == "Travaux":
        candidats = [chunk for chunk in chunks if chunk["metadata"]["has_price"]]
    elif keyword == "Département":
        candidats = [chunk for chunk in chunks if chunk["metadata"]["has_postal_code"]]
    elif keyword == "Type":
        candidats = [chunk for chunk in chunks if chunk["metadata"]["has_offer_type"]]
    elif keyword == "Nature":
        candidats = [chunk for chunk in chunks if chunk["metadata"]["has_nature_operation"]]
    elif keyword == "Master_work":
        candidats = [chunk for chunk in chunks if chunk["metadata"]["has_master_work"]]
    elif keyword == "Mandataire" or keyword == "Mandataire-requis":
        candidats = [chunk for chunk in chunks if chunk["metadata"]["has_mandataire_requis"]]
    elif keyword == "Exclusivité":
        candidats = [chunk for chunk in chunks if chunk["metadata"]["has_exclusivity"]]
    elif keyword == "Visite":
        candidats = [chunk for chunk in chunks if chunk["metadata"]["has_visite"]]
    elif keyword == "Compétences":
        candidats = [chunk for chunk in chunks if chunk["metadata"]["has_competences"]]
    elif keyword == "Missions":
        candidats = [chunk for chunk in chunks if chunk["metadata"]["has_missions"]]
    elif keyword == "Maquette":
        candidats = [chunk for chunk in chunks if chunk["metadata"]["has_maquette"]]
    elif keyword == "Film":
        candidats = [chunk for chunk in chunks if chunk["metadata"]["has_film"]]
    elif keyword == "Références":
        candidats = [chunk for chunk in chunks if chunk["metadata"]["has_références"]]
    elif keyword == "Tranches":
        candidats = [chunk for chunk in chunks if chunk["metadata"]["has_tranches"]]
    elif keyword == "Intervention":
        candidats = [chunk for chunk in chunks if chunk["metadata"]["has_intervention"]]
    elif keyword == "Seconde échéance":
        candidats = [chunk for chunk in chunks if chunk["metadata"]["has_second_deadline"]]
    elif keyword == "Numéro":
        candidats = [chunk for chunk in chunks if chunk["metadata"]["has_number"]]
    elif keyword == "Type d'opération":
        candidats = [chunk for chunk in chunks if chunk["metadata"]["has_operation_type"]]
    else:
        return embeddings, chunks
    candidats_emb = [embeddings[chunk["metadata"]["id"]] for chunk in candidats if len(candidats) > 0]
    return candidats_emb, candidats

################################################################################################
def main_loop(embeddings, questions_rag, chunks):
    q_r = {}
    data = [()]
    epci = str()
    header = chunks[0]["text"] + "\n\n" + chunks[1]["text"]
    for i in range(len(questions_rag)):
        # if True:
        if i == 11:
            
            question_emb = np.array(ollama.embeddings(model="nomic-embed-text", prompt=questions_rag[i]["rerank"])["embedding"])
            addMetaData(chunks)
            data_embed, candidats = match_metadata(questions_rag[i]["keyword"], chunks, embeddings)
            similarities = [cosine_similarity(question_emb, emb) for emb in data_embed]
            top_10 = np.argsort(similarities)[-10:][::-1]
            
            best_chunks = []
            for idx in top_10:
                best_chunks.append(candidats[idx]["text"])
            # print("SALUT")
            
            reranked_chunks = rerank(questions_rag[i]["rerank"], best_chunks)[:5]
            if questions_rag[i]["keyword"] == "Mandataire":
                merged_context = header
            else:
                merged_context = "\n\n".join(f"EXTRAIT{j + 1}:\n{chunk[0]}" for j, chunk in enumerate(reranked_chunks))
            print(f"QUESTION = {questions_rag[i]['llm']}\n\nmerged_context = {merged_context}", flush=True)
            print(f"Questions n° {i + 1}/{len(questions_rag)}")
            answer = send_playload(questions_rag, merged_context, i)
            if questions_rag[i]["keyword"] == "Ouvrage":
                id_ouvrage = answer 

            # if questions_rag[i]["keyword"] == "Ville":
            #     epci = get_epci(answer)["nom"]
            #     answer = epci + "\n" + answer
            
            if questions_rag[i]["keyword"] == "Mandataire":
                # total_id = epci + "\n" + id_ouvrage + "\n" + answer
                data.append(("Identification de l'acheteur", answer))

            elif questions_rag[i]["keyword"] == "Type d'opération":
                etat = [False, False, 0]
                data.append(("Type d'opération", answer))
                # data.append(("Objet de la candidature", etat))
                # data.append(("Présentation du candidat", ""))
            
            q_r[questions_rag[i]["user"]] = answer
    
    return q_r, data
