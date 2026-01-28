import re
import sys

META_DATA = [
    {
        "numero": 0,

    }
]

def code_postale(chunk):
    if re.search(r"\d{5}", chunk):
        new = "RENSEIGNEMENTS:\nCe texte contient probablement un code postale"


fonctions_meta_donnees = {
    code_postale,
}

def classify(chunk):