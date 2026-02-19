"""
Reçoit un payload plat DC2 (une clé par champ, aucun sous-dictionnaire).
Génère DC2.docx à partir du template.
"""
import os
from docxtpl import DocxTemplate


def create_dc2(body: dict) -> dict:
    """
    Le body est déjà plat. On normalise chaque valeur en str pour docxtpl.
    """
    data = {}
    for k, v in body.items():
        if v is None:
            data[k] = ""
        elif isinstance(v, str):
            data[k] = v
        else:
            data[k] = str(v)
    return data


def fill_dc2(data: dict) -> None:
    """Génère le document DC2.docx à partir du template et des données (clés à la racine)."""
    for k, v in data.items():
        print(k, v)
        print("--------------------------------")
    base = os.path.dirname(__file__)
    template_path = os.path.join(base, "Documents", "DC2.docx")
    output_dir = os.path.join(base, "output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "dc2.docx")

    if not os.path.isfile(template_path):
        raise FileNotFoundError(
            f"Template DC2 non trouvé : {template_path}. "
            "Créez le dossier backend/Documents/ et placez DC2.docx dedans."
        )

    doc = DocxTemplate(template_path)
    doc.render(data)
    doc.save(output_path)
