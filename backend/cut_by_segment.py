import os
import re
import unicodedata


def delete_sommaire(text):
    segments = text.split("\n")
    in_sommaire = 0
    SOMMAIRE_PATTERN = re.compile(r"^SOMMAIRE\s*$", re.IGNORECASE)
    to_delete = []
    for segment in segments:
        if in_sommaire == 1 and re.search(r"\d$", segment):
            to_delete.append(segment)
            print(segment)

        elif in_sommaire == 1 and not re.search(r"\d$", segment):
            in_sommaire = 0

        if re.search(SOMMAIRE_PATTERN, segment) and in_sommaire == 0:
            in_sommaire = 1
            to_delete.append(segment)
    for delete in to_delete:
        segments.remove(delete)
    # print(segments)
    return segments

def cut_by_segment(text):
    to_push = str()
    res = []
    text = str(text) if text is not None else ""
    segments = text.split("\n")
    SOMMAIRE_PATTERN = re.compile(r"^SOMMAIRE\s*$", re.IGNORECASE | re.MULTILINE)
    print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\n")
    print(type(text))

    # Détection sommaire : normaliser (NFKC + espaces) pour gérer PDF (espaces insécables, caractères spéciaux)
    # text_norm = unicodedata.normalize("NFKC", text).replace("\u00a0", " ").lower()
    if "sommaire" in text.lower():
        segments = delete_sommaire(text)

    SEGMENT_PATTERN = r"^\d+\.\d+(\.\d+)*\s"
    ARTICLE_PATTERN = r"^ARTICLE\s+\d+"
    to_know = 0

    for segment in segments:
        # if "SOMMAIRE" in segment:
        #     to_know = 1
        # if to_know == 1:
        if re.search(ARTICLE_PATTERN, segment) or re.search(SEGMENT_PATTERN, segment):
            res.append(to_push)
            to_push = segment + "\n"
        else:
            to_push += segment + "\n"
    res.append(to_push)
    # print(res)
    return res

