import re
import os
import unicodedata

def add_price_metadata(chunk):
    PRICE_PATTERN = re.compile(
    r"(?<!\w)"                              # pas collé à une lettre
    r"(?:€\s*)?"                            # € optionnel avant
    r"(?:\d{1,3}(?:[ .]\d{3})+|\d+)"        # nombre OU milliers
    r"(?:[.,]\d{2})?"                       # centimes optionnels
    r"\s*€"                                 # € OBLIGATOIRE après
    r"(?!\w)"                               # pas collé à une lettre
    )

    MILLION_PATTERN = re.compile(
    r"\b\d{1,3}\s+millions?\s+d['’]euros\b",
    re.IGNORECASE
    )

    if re.search(PRICE_PATTERN, chunk["text"]) or re.search(MILLION_PATTERN, chunk["text"]):
        chunk["metadata"]["has_price"] = True

def add_date_metadata(chunk):
    mois = "janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre"
    DATE_PATTERN = r"\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b"
    DATE_PATTERN2 = rf"\b\d{{1,2}}\s(?:{mois})\s\d{{4}}\b"

    if re.search(DATE_PATTERN, chunk["text"]) or re.search(DATE_PATTERN2, chunk["text"]):
        chunk["metadata"]["has_date"] = True

def add_postal_code_metadata(chunk):
    POSTAL_CODE_PATTERN = r"\b\d{2}\s?\d{3}\b"
    DEPARTMENT_PATTERN = r"\((0[1-9]|[1-8][0-9]|9[0-5]|97[1-6]|98[4-8])\)"

    if re.search(POSTAL_CODE_PATTERN, chunk["text"]) or re.search(DEPARTMENT_PATTERN, chunk["text"]):
        chunk["metadata"]["has_postal_code"] = True

def add_offer_type_metadata(chunk):
    OFFER_TYPE_PATTERN = re.compile(
        r"\b(?:appel à candidatures|appel d'offres)\b",
        re.IGNORECASE,
    )
    if re.search(OFFER_TYPE_PATTERN, chunk["text"]):
        chunk["metadata"]["has_offer_type"] = True
 
def add_nature_operation_metadata(chunk):
    NATURE_OPERATION_PATTERN = re.compile(
        r"\b(?:construction neuve|extension|réhabilitation|rénovation|restructuration)\b",
        re.IGNORECASE,
    )
    if re.search(NATURE_OPERATION_PATTERN, chunk["text"]):
        chunk["metadata"]["has_nature_operation"] = True

def add_master_work_metadata(chunk):
    MASTER_WORK_PATTERN = re.compile(
        r"\b(?:maître d'ouvrage|maître|ouvrages|ouvrage|maître de l'ouvrage)\b",
        re.IGNORECASE
    )
    if re.search(MASTER_WORK_PATTERN, chunk["text"]):
        chunk["metadata"]["has_master_work"] = True

def add_mandataire_metadata(chunk):
    MANDATAIRE_PATTERN = re.compile(
        r"\b(?:mandataire|Téléphone|@)\b",
        re.IGNORECASE
    )
    if re.search(MANDATAIRE_PATTERN, chunk["text"]):
        chunk["metadata"]["has_mandataire"] = True
        # print(f"TEXTE == {chunk['text']}\n")

def add_mandataire_requis_metadata(chunk):
    MANDATAIRE_REQUIS_PATTERN = re.compile(
        r"\b(?:mandataire requis)\b",
        re.IGNORECASE
    )
    if re.search(MANDATAIRE_REQUIS_PATTERN, chunk["text"]):
        chunk["metadata"]["has_mandataire_requis"] = True


def add_exclusivity_metadata(chunk):
    EXCLUSIVITY_PATTERN = re.compile(
        r"\b(?:exclusivité|bureaux d'études|bureaux|exclusif)\b",
        re.IGNORECASE
    )
    if re.search(EXCLUSIVITY_PATTERN, chunk["text"]):
        chunk["metadata"]["has_exclusivity"] = True

def add_visite_metadata(chunk):
    VISITE_PATTERN = re.compile(
        r"\b(?:visite|rendez-vous|déplacement sur site)\b",
        re.IGNORECASE
    )
    if re.search(VISITE_PATTERN, chunk["text"]):
        chunk["metadata"]["has_visite"] = True

def add_competences_metadata(chunk):
    COMPETENCES_PATTERN = re.compile(
        r"\b(?:compétences|spécialités)\b",
        re.IGNORECASE
    )
    if re.search(COMPETENCES_PATTERN, chunk["text"]):
        chunk["metadata"]["has_competences"] = True

def add_missions_metadata(chunk):
    MISSIONS_PATTERN = re.compile(
        r"\b(?:missions|missions requises| DIAG| FAISA| REL| EXE| mission complète)\b",
        re.IGNORECASE
    )
    if re.search(MISSIONS_PATTERN, chunk["text"]):
        chunk["metadata"]["has_missions"] = True

def add_maquette_metadata(chunk):
    MAQUETTE_PATTERN = re.compile(
        r"\b(?:maquette|maquette numérique|maquette physique)\b",
        re.IGNORECASE
    )
    if re.search(MAQUETTE_PATTERN, chunk["text"]):
        chunk["metadata"]["has_maquette"] = True

def add_film_metadata(chunk):
    FILM_PATTERN = re.compile(
        r"\b(?:film|film de présentation)\b",
        re.IGNORECASE
    )
    if re.search(FILM_PATTERN, chunk["text"]):
        chunk["metadata"]["has_film"] = True

def add_references_metadata(chunk):
    REFERENCES_PATTERN = re.compile(
        r"\b(?:références|références professionnelles|référence)\b",
        re.IGNORECASE,
    )
    # Normaliser en NFC pour matcher même si le PDF a fourni du NFD (é = e + accent)
    text_nfc = unicodedata.normalize("NFC", chunk["text"])
    if re.search(REFERENCES_PATTERN, text_nfc):
        chunk["metadata"]["has_references"] = True

def add_tranches_metadata(chunk):
    TRANCHES_PATTERN = re.compile(
        r"\b(?:tranches|tranche ferme|tranche optionnelle)\b",
        re.IGNORECASE
    )
    if re.search(TRANCHES_PATTERN, chunk["text"]):
        chunk["metadata"]["has_tranches"] = True

def add_second_deadline_metadata(chunk):
    SECOND_DEADLINE_PATTERN = re.compile(
        r"\b(?:seconde échéance)\b",
        re.IGNORECASE
    )
    if re.search(SECOND_DEADLINE_PATTERN, chunk["text"]):
        chunk["metadata"]["has_second_deadline"] = True

def add_number_metadata(chunk):
    NUMBER_PATTERN = re.compile(
        r"\b(?:numéro|n°|numéro de consultation|n° de consultation)\b",
        re.IGNORECASE
    )
    if re.search(NUMBER_PATTERN, chunk["text"]):
        chunk["metadata"]["has_number"] = True

def add_operation_type_metadata(chunk):
    OPERATION_TYPE_PATTERN = re.compile(
        r"\b(?:MARCHE|Opération)\b",
        re.IGNORECASE
    )
    if re.search(OPERATION_TYPE_PATTERN, chunk["text"]):
        chunk["metadata"]["has_operation_type"] = True

def add_keyword_metadata(chunk, keyword):
    if keyword in chunk["text"]:
        chunk["metadata"]["has_keyword"] = True