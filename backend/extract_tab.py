import pandas as pd 


def create_ref():
    ref = {
        "nom_projet" : "",
        "equipe_interne": "",
        "statut_projet": "",
        "annee_conception": "",
        "annee_livraison": "",
        "ville": "",
        "departement": "",
        "region": "",
        "pays": "",
        "type_programme": "",
        "sous_type": "",
        "typologie": "",
        "maitre_ouvrage": "",
        "type_maitre_ouvrage": "",
        "surface_sdp": "",
        "surface_shab": "",
        "cout_travaux": "",
        "cout_m2": "",
        "duree_chantier": "",
        "niveaux": "",
        "nombre_logements": "",
        "materiau_principal": "",
        "structure_principal": "",
        "label_environnemental": "",
        "mission_agence": "",
        "liste_mission": "",
        "partenaires": "",
        "entreprise_type": "",
        "type_marche": "",
        "millieu_occupe": "",
        "patrimoine": "",
        "rehabilitation": "",
        "extension": "",
        "construction_neuve": "",
        "renovation_thermique": "",
        "BIM": "",
        "RE2020": "",
        "complexite": "",
        "mots_cles": "",
        "resume_projet": "",
        "points_fort": "",
        "contraintes_majeur": "",
        "parti_architectural": "",
        "innovation_technique": "",

    }

def extract_db(path="backend/Documents/DB_PROJETS_ALU.xlsx"):
    data = pd.read_excel(path)

