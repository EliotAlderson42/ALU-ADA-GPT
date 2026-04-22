from reportlab.platypus import *

"""
Reception et normalisation des donnees memoire technique envoyees par le frontend.
La generation PDF est volontairement desactivee ici.
"""


def _to_str(value) -> str:
    if value is None:
        return ""
    return str(value)


def create_memoire_payload(body: dict) -> dict:
    """Normalise le payload recu du frontend."""
    payload = body if isinstance(body, dict) else {}
    return {
        "title": _to_str(payload.get("title")) or "MEMOIRE TECHNIQUE",
        "group_label": _to_str(payload.get("group_label")),
        "project_title": _to_str(payload.get("project_title")),
        "intro": _to_str(payload.get("intro")),
        "chapters": payload.get("chapters") if isinstance(payload.get("chapters"), list) else [],
    }


def fill_memoire_docx(payload: dict) -> None:
    """
    Conserve le nom historique de fonction pour compatibilite API.
    Ne genere plus de PDF : le traitement de sortie est gere ailleurs.
    """
    doc = BaseDocTemplate("Note-Methodologique.pdf")

    
    _ = payload
    return None
