import pandas as pd 

#IDEES:
#1: Demander au llm de faire un resumer de chaque references les foutres dans une dbv et les comparer avec le rendu de la reponse
#2:

def create_ref(row):
    ref = {
        "id_projet": "",
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
        "innovation_technique": ""
    }
    
    for i, key in enumerate(ref):
        ref[key] = row[i]
    
    # print(ref)
    return ref

def give_score(json, db):
    score_tab = []
    for ref in db:
        score = 0
        for key, value in ref.items():
            if json[key] == value:
                score += 1
        score_tab.append(score)
    return score_tab


def extract_db(path="backend/Documents/DB_PROJETS_ALU.xlsx"):
    # res = db
    res = []
    data = pd.read_excel(path)
    for row in data.values:
        res.append(create_ref(row))
        print("0000000000000000000000")
        print(row)
        print("0000000000000000000000")


    for r in res:
        print(r)
        print("-----------------------------------------")
    print(f"TAAAAAILLE = {len(res)}")
    return res


def clear_row(row):
    row = row.replace("'", "")
    row = row.split()


# def match_references(json):

