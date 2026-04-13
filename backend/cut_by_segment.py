import os
import re
import unicodedata
from backend.extract_tab import extract_db

def chunk_text(text, chunk_size=300, overlap=50):
    words = text.split()
    chunks = []
    start = 0
    i = 0

    while start < len(words):
        end = start + chunk_size

        chunk_text_str = " ".join(words[start:end])

        # chunk = {
        #     "text": chunk_text_str,
        #     "metadata": {
        #         "id": i,
        #         "has_postal_code": False,
        #         "has_price": False,
        #         "has_date": False,
        #         "has_offer_type": False,
        #         "has_nature_operation": False,
        #         "has_master_work": False,
        #         "has_mandataire": False,
        #         "has_mandataire_requis": False,
        #         "has_exclusivity": False,
        #         "has_visite": False,
        #         "has_competences": False,
        #         "has_missions": False,
        #         "has_maquette": False,
        #         "has_film": False,
        #         "has_references": False,
        #         "has_tranches": False,
        #         "has_second_deadline": False,
        #         "has_number": False,
        #         "has_operation_type": False,
        #         "has_keyword": False,
        #         # "has_intervention": False,
        #     },
        # }

        chunks.append(chunk_text_str)

        start += chunk_size - overlap
        i += 1

    return chunks

def middle_split(text):
    res = []
    length = len(text) // 2
    first_half = text[:length]
    second_half = text[length:]
    res.append(first_half)
    res.append(second_half)
    return res

def next_line_is_summary(i, segments):
    if i + 2 < len(segments) - 1:
        if "........" in segments[i + 1] or "........" in segments[i + 2] or re.search(r"\d{8}", segments[i]):
            return True
    return False

def delete_sommaire(text):
    segments = text.split("\n")
    to_delete = []
    for i, segment in enumerate(segments):
        if "........" in segment or next_line_is_summary(i, segments):
            to_delete.append(segment)
    for delete in to_delete:
        print(f"DELETE = {delete}")
        segments.remove(delete)
    return segments

def create_chunk(text, id):
    return {
        "text": text,
        "metadata": {
            "id": id,
            "has_postal_code": False,
            "has_price": False,
            "has_date": False,
            "has_offer_type": False,
            "has_nature_operation": False,
            "has_master_work": False,
            "has_mandataire": False,
            "has_mandataire_requis": False,
            "has_exclusivity": False,
            "has_visite": False,
            "has_competences": False,
            "has_missions": False,
            "has_maquette": False,
            "has_film": False,
            "has_references": False,
            "has_tranches": False,
            "has_second_deadline": False,
            "has_number": False,
            "has_operation_type": False,
            "has_keyword": False,
            "has_methodologie": False,
            # "has_intervention": False,
        },
    }

def cut_again(text, number):
    to_push = ""
    res = []
    exxit = 0
    index = -1

    patterns = [
        re.compile(r"^[a-z]\)", re.IGNORECASE),  # a)
        re.compile(r"^\d+\)"),    # 1)
        re.compile(r"^[a-z]\.", re.IGNORECASE),  # a.
        re.compile(r"^\d+\."),    # 1.
        re.compile(r"^\d+[.-]\d+"),    # 1-1
        re.compile(r"^\d+°"),
        re.compile(r"^[a-z]\-", re.IGNORECASE),  # a-
        re.compile(r"^Dossier\s+(\d+|[IVXLCDM]+)", re.IGNORECASE),
        # re.compile(r"^\d+\.\d+"),    # 1.1
    ]
    text_list = text.split("\n")
    # for t in text_list:
        # print(f"COUUUUPER === {t}")
    # save = text_list[0]
    # text_list.pop(0)
    for texte in text_list[1:]:
        for pattern in patterns:
            if re.search(pattern, texte):
                print(f"PHRAAAAAAASE = {texte}")
                exxit = 1
                index = patterns.index(pattern)
                break
        if exxit == 1:
            break
    if index:    
        print(f"INDEX == {index} DEBUT === {text_list[0]}")
    elif index == -1:
        return chunk_text(text)
    if exxit == 1:
        for texte in text_list:
            if re.search(patterns[index], texte) and len(texte) > 0:
                res.append(to_push)
                to_push = texte + "\n"
            else:
                to_push += texte + "\n"
        res.append(to_push)
        return res
    else:
        return text

def cut_by_segment(text):
    # extract_db()
    # return 0
    to_push = ""
    num = 0
    # res = []
    chunks = []
    segments = text.split("\n")

    if "sommaire" in text.lower():
        segments = delete_sommaire(text)

    # SEGMENT_PATTERN = r"^\d+\.\d+(\.\d+)"
    start = ["ARTICLE", "SEGMENT", "1.", "SECTION"]
    # print(f"TO_KNOW == {int(start[2]) + 1}")
    pattern = [
         re.compile(r"^Article\s+(\d+|[IVXLCDM]+)", re.IGNORECASE),
         re.compile(r"^Segment\s+(\d+|[IVXLCDM]+)", re.IGNORECASE),
         re.compile(r"^\d\.\s"),
         re.compile(r"^Section\s+(\d+|[IVXLCDM]+)", re.IGNORECASE),
    ]


    id_chunk = 0
    #Recherche du Regex a utiliser
    for segment in segments:
        mots = segment.split(" ")
        if mots[0].upper() in start:
            index = start.index(mots[0].upper())
            if index == 2:
                num = 1
            break      


    for segment in segments:
        if re.search(pattern[index], segment):
            # cut = to_push.split(" ")
            if len(to_push) >= 5000:
                lst = cut_again(to_push, None)
                to_push = segment + "\n"
                if isinstance(lst, str) and len(lst) > 0:
                    chunks.append(create_chunk(lst, id_chunk))
                    id_chunk += 1
                else:
                    for l in lst:
                        if len(l) > 0:
                            chunks.append(create_chunk(l, id_chunk))
                            id_chunk += 1
            elif len(to_push) > 0:
                chunks.append(create_chunk(to_push, id_chunk))
                to_push = segment + "\n"
                id_chunk += 1
        else:
            to_push += segment + "\n"

    if len(to_push) >= 5000:

        cut = to_push.split(" ")
        print(f"CUUT = {cut[1]}")
        # lst = cut_again(to_push, int(cut[1]))
        lst = cut_again(to_push, None)

        for l in lst:
            chunks.append(create_chunk(l, id_chunk))
            id_chunk += 1
    else:
        chunks.append(create_chunk(to_push, id_chunk))
    res = []
    id = 0
    for chunk in chunks:
        if len(chunk["text"]) > 5000:
            lst = cut_again(chunk["text"], None)
            if isinstance(lst, str):
                res.append(chunk)
                id += 1
            else:
                for l in lst:
                    print(f"CUTLIST == {l}")
                    res.append(create_chunk(l, id))
                    id += 1
        else:
            res.append(chunk)
            id += 1
        # for r in res:
        #     print(f"lenchunk = {len(r["text"])} content = {r["text"]}")
    return res

