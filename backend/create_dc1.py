"""
Transforme le payload frontend DC1 en dictionnaire plat pour le template Word.
Utilise les données du formulaire DC1 (pas de valeurs prédéfinies).
"""
import os
from docxtpl import DocxTemplate


def create_dc1(body: dict) -> dict:
    """
    Extrait et aplatit les données du payload frontend pour le template DC1.docx.
    Toutes les valeurs du formulaire sont utilisées (aucune donnée prédéfinie).
    """
    data = {}

    # moduleA, moduleB : clé-valeur (keyword -> answer)
    for mod_key in ("moduleA", "moduleB"):
        mod = body.get(mod_key) or {}
        for k, v in mod.items():
            if isinstance(v, dict):
                for k2, v2 in v.items():
                    data[k2] = v2
            else:
                data[k] = v

    # moduleC : objetCandidature, lotNumero, intituleLots
    mod_c = body.get("moduleC") or {}
    for k, v in mod_c.items():
        if isinstance(v, dict):
            for k2, v2 in v.items():
                data[k2] = v2
        else:
            data[k] = v

    # moduleD : presentation, groupementType, mandataireSolidaire, candidate
    mod_d = body.get("moduleD") or {}
    for k, v in mod_d.items():
        if k == "candidate" and isinstance(v, dict):
            for ck, cv in v.items():
                data[ck] = cv
        elif isinstance(v, dict):
            for k2, v2 in v.items():
                data[k2] = v2
        else:
            data[k] = v

    # moduleE : lotNumero_1, identifications_1, prestations_1, etc.
    mod_e = body.get("moduleE") or {}
    if isinstance(mod_e, dict):
        for k, v in mod_e.items():
            data[k] = v

    # moduleF : f1ExclusionChecked, f2AdresseInternet, etc.
    mod_f = body.get("moduleF") or {}
    for k, v in mod_f.items():
        if isinstance(v, dict):
            for k2, v2 in v.items():
                data[k2] = v2
        else:
            data[k] = v

    # moduleG : mandataire (préfixe pour ne pas écraser candidat)
    mod_g = body.get("moduleG") or {}
    mand = mod_g.get("mandataire")
    if isinstance(mand, dict):
        for mk, mv in mand.items():
            data[f"mandataire_{mk}"] = mv

    # Conversion en str pour docxtpl (évite les erreurs)
    for k in list(data.keys()):
        if data[k] is None:
            data[k] = ""
        elif not isinstance(data[k], str):
            data[k] = str(data[k])

    # Alias snake_case pour compatibilité template (ex: nom_commercial_denomination)
    # _camel_to_snake = lambda s: "".join("_" + c.lower() if c.isupper() else c for c in s).lstrip("_")
    # for k in list(data.keys()):
    #     if "_" not in k and k[0].islower():
    #         snake = _camel_to_snake(k)
    #         if snake not in data:
    #             data[snake] = data[k]
    for k,v in data.items():
        print(k,v)
        print("--------------------------------")
        print("--------------------------------")
    return data


def fill_dc1(data: dict) -> None:
    """Génère le document DC1.docx à partir du template et des données."""
    base = os.path.dirname(__file__)
    template_path = os.path.join(base, "Documents", "DC1.docx")
    output_dir = os.path.join(base, "output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "dc1.docx")

    if not os.path.isfile(template_path):
        raise FileNotFoundError(
            f"Template DC1 non trouvé : {template_path}. "
            "Créez le dossier backend/Documents/ et placez DC1.docx dedans."
        )

    doc = DocxTemplate(template_path)
    doc.render(data)
    doc.save(output_path)
