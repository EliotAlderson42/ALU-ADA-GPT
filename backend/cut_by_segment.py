import os
import re
import unicodedata
from backend.extract_tab import extract_db

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
            "id": 0,
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
            # "has_intervention": False,
        },
    }

def cut_again(text, number):
    # print(f"NUMBER = {number}")
    # if number:
    #     suite =  ["a)", "1)", "a.", "1.", f"{number}-1", f"{number}.1"]
    #     patterns = [
    #         re.compile(r"^[a-z]\)", re.IGNORECASE),  # a)
    #         re.compile(r"^\d+\)"),    # 1)
    #         re.compile(r"^[a-z]\.", re.IGNORECASE),  # a.
    #         re.compile(r"^\d+\."),    # 1.
    #         re.compile(rf"^{number}+-\d+"),    # 1-1
    #         re.compile(rf"^{number}+\.\d+"),    # 1.1
    #     ]
        
    # else:
    #     suite =  ["a)", "1)", "a.", "1.", "1-1", "1.1"]
    to_push = ""
    res = []
    exxit = 0

    patterns = [
        re.compile(r"^[a-z]\)", re.IGNORECASE),  # a)
        re.compile(r"^\d+\)"),    # 1)
        re.compile(r"^[a-z]\."),  # a.
        re.compile(r"^\d+\."),    # 1.
        re.compile(r"^d+-\d+"),    # 1-1
        re.compile(r"^d+\.\d+"),    # 1.1
    ]
    text_list = text.split("\n")
    for texte in text_list:
        for pattern in patterns:
            if re.search(pattern, texte):
                print(f"PHRAAAAAAASE = {texte}")
                exxit = 1
                index = patterns.index(pattern)
                break
        if exxit == 1:
            break

    for text in text_list:
        if re.search(patterns[index], text):
            # print(f"TOPUUUUUUSH = {to_push}")
            res.append(to_push)
            to_push = text + "\n"
        else:
            to_push += text + "\n"
    res.append(to_push)
    return res

def cut_by_segment(text):
    # extract_db()
    # return 0
    to_push = ""
    # res = []
    chunks = []
    segments = text.split("\n")

    if "sommaire" in text.lower():
        print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\n")
        segments = delete_sommaire(text)

    # SEGMENT_PATTERN = r"^\d+\.\d+(\.\d+)"
    start = ["ARTICLE", "SEGMENT"]
    pattern = [
         re.compile(r"^Article\s+(\d+|[IVXLCDM]+)", re.IGNORECASE),
         re.compile(r"^Segment\s+(\d+|[IVXLCDM]+)", re.IGNORECASE),
    ]


    id_chunk = 0
    #Recherche du Regex a utiliser
    for segment in segments:
        mots = segment.split(" ")
        if mots[0].upper() in start:
            index = start.index(mots[0].upper())
            break      


    for segment in segments:
        if re.search(pattern[index], segment):
            cut = to_push.split(" ")
            if len(to_push) >= 5000:
                # print(f"CUUUUUUUUUTIE == {cut[1]}")
                # if cut[1] >= '0' and cut[1] <= '9':
                #     lst = cut_again(to_push, int(cut[1]))
                # else: 
                lst = cut_again(to_push, None)

                to_push = segment + "\n"
                
                for l in lst:
                    chunks.append(create_chunk(l, id_chunk))
                    id_chunk += 1
            else:
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

    for r in chunks:
        print(r["text"])
        print(f"TAILLE = {len(r["text"])}")
        print("--------------------------------")
        print("--------------------------------")
    print(f"TAILLE = {len(chunks)}")
    # print(res)
    return chunks

