import pandas as pd 

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

def extract_db(path="backend/Documents/DB_PROJETS_ALU.xlsx"):
    
    # res = db
    res = []
    data = pd.read_excel(path)
    # print(data.head())
    # print(data.columns)
    # print(data.info())
    for row in data.values:
        res.append(create_ref(row))
        print("0000000000000000000000")
        print(row)
        print("0000000000000000000000")


    for r in res:
        print(r)
        print("-----------------------------------------")
    print(f"TAAAAAILLE = {len(res)}")


def clear_row(row):
    row = row.replace("'", "")
    row = row.split()

