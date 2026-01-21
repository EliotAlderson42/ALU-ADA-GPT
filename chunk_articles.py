def split_points(text):
    POINT_PATTERN = re.compile(r'(?:^|/n)([A-Z])\.\s+')
    parts = POINT_PATTERN.split(text)
    points = []

    for i in range(1, len(parts), 2):
        letter = parts[i]
        content = parts[i + 1].strip()
        points.append((letter, content))
    return points


ARTICLE_PATTERN = re.compile(
    r'(ARTICLE\s+\d+\s*[-–]\s*[A-ZÀ-ÖØ-Ý ].+)',
    re.IGNORECASE
)

#Fonction pour decouper le pdf en plusieurs articles
def split_articles(text:str):
    parts = ARTICLE_PATTERN.split(text)
    for part in parts:
        print(part)
        print("------------------------------------")
    articles = []

    intro_text = parts[0].strip()
    if intro_text:
        articles.append((
            "PREAMBULE - INFORMATIONS GENERALES",
            intro_text
        ))
    for i in range(1, len(parts), 2):
        title = parts[i].strip()
        content = parts[i + 1].strip() if i+1 < len(parts) else ""
        articles.append((title, content))
    return articles

# Regex pour détecter les articles
ARTICLE_PATTERN = re.compile(r'ARTICLE\s+\d+\s*[-–]\s*[A-ZÀ-ÖØ-Ý ].+', re.IGNORECASE)

# Regex pour détecter les points A., B., C.
POINT_PATTERN = re.compile(r'(?:^|\n)\s*([A-Z])[\.\)]\s+')

def classify_chunk(text: str) -> str:
    text = text.lower()
    if any(k in text for k in ["coût", "montant", "€", "euro"]):
        return "FINANCIER"
    if any(k in text for k in ["date", "délai", "remise"]):
        return "PLANNING"
    if any(k in text for k in ["procédure", "concours", "appel d’offres"]):
        return "PROCEDURE"
    if any(k in text for k in ["mission", "compétence", "référence"]):
        return "MISSIONS"
    return "GENERAL"

# def chunk_pdf(path: str):
#     chunks = []
#     with pdfplumber.open(path) as pdf:
#         current_title = None
#         current_content = ""
#         first_article_found = False
#         preamble_content = ""

#         # Parcours toutes les pages
#         for page_num, page in enumerate(pdf.pages, start=1):
#             text = page.extract_text()
#             if not text:
#                 continue
#             lines = text.split("\n")
#             for line in lines:
#                 line_clean = line.strip()
#                 if ARTICLE_PATTERN.match(line_clean):
#                     if not first_article_found:
#                         # Tout ce qui précède le premier ARTICLE = préambule
#                         if preamble_content.strip():
#                             chunks.append((
# "PREAMBULE – INFORMATIONS GENERALES",
# preamble_content.strip(),
# f"1-{page_num-1}"
# ))
#                         first_article_found = True

#                     # Sauvegarde l'article précédent
#                     if current_title:
#                         chunks.append((current_title, current_content.strip(), page_num))
#                     current_title = line_clean
#                     current_content = ""
#                 else:
#                     if not first_article_found:
#                         # On accumule le préambule
#                         preamble_content += line + "\n"
#                     else:
#                         # On accumule le contenu de l'article
#                         current_content += line + "\n"

#         # Ajouter le dernier article
#         if current_title:
#             chunks.append((current_title, current_content.strip(), page_num))

#         # Découpage points A/B/C pour chaque article
#         final_chunks = []
#         for article_title, article_content, page_num in chunks:
#             points = POINT_PATTERN.split(article_content)
#             if len(points) > 1:
#                 # points détectés
#                 for j in range(1, len(points), 2):
#                     letter = points[j]
#                     content = points[j+1].strip()
#                     chunk_type = classify_chunk(content)
#                     final_chunks.append(f"""
# [TYPE: {chunk_type}]
# [ARTICLE: {article_title}]
# [POINT: {letter}]
# [PAGE: {page_num}]

# {content}
# """.strip())
#             else:
#                 # Pas de point détecté, tout l'article comme un chunk
#                 chunk_type = classify_chunk(article_content)
#                 final_chunks.append(f"""
# [TYPE: {chunk_type}]
# [ARTICLE: {article_title}]
# [POINT: NA]
# [PAGE: {page_num}]

# {article_content}
# """.strip())

#     return final_chunks

def chunk_pdf(path: str):
    chunks = []
    with pdfplumber.open(path) as pdf:
        current_title = None
        current_content = ""
        first_article_found = False
        preamble_content = ""

        # Parcours toutes les pages
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if not text:
                continue
            lines = text.split("\n")
            for line in lines:
                line_clean = line.strip()
                if ARTICLE_PATTERN.match(line_clean):
                    if not first_article_found:
                        # Tout ce qui précède le premier ARTICLE = préambule
                        if preamble_content.strip():
                            chunks.append((
                                "PREAMBULE – INFORMATIONS GENERALES",
                                preamble_content.strip(),
                                f"1-{page_num-1}"
                            ))
                        first_article_found = True

                    # Sauvegarde l'article précédent
                    if current_title:
                        chunks.append((current_title, current_content.strip(), page_num))
                    current_title = line_clean
                    current_content = ""
                else:
                    if not first_article_found:
                        # On accumule le préambule
                        preamble_content += line + "\n"
                    else:
                        # On accumule le contenu de l'article
                        current_content += line + "\n"

        # Ajouter le dernier article
        if current_title:
            chunks.append((current_title, current_content.strip(), page_num))

        # Découpage points A/B/C pour chaque article
        final_chunks = []
        for article_title, article_content, page_num in chunks:
            points = POINT_PATTERN.split(article_content)
            if len(points) > 1:
                # texte avant le premier point
                intro_text = points[0].strip()
                if intro_text:
                    chunk_type = classify_chunk(intro_text)
                    final_chunks.append(f"""
[TYPE: {chunk_type}]
[ARTICLE: {article_title}]
[POINT: INTRO]
[PAGE: {page_num}]

{intro_text}
""".strip())

                # ensuite les points A/B/C
                for j in range(1, len(points), 2):
                    letter = points[j]
                    content = points[j+1].strip()
                    chunk_type = classify_chunk(content)
                    final_chunks.append(f"""
[TYPE: {chunk_type}]
[ARTICLE: {article_title}]
[POINT: {letter}]
[PAGE: {page_num}]

{content}
""".strip())
            else:
                # Pas de point détecté, tout l'article comme un chunk
                chunk_type = classify_chunk(article_content)
                final_chunks.append(f"""
[TYPE: {chunk_type}]
[ARTICLE: {article_title}]
[POINT: NA]
[PAGE: {page_num}]

{article_content}
""".strip())

    return final_chunks



def travelTime(ville):
    name = ville.split()
    name = name[0] + ", France"

    geolocator = Nominatim(user_agent="my_geocoder")
    data = geolocator.geocode(city)
    data1 = geolocator.geocode("Epinay-sur-Orge, France")
    url = f"http://router.project-osrm.org/route/v1/driving/{data1.latitude},{data1.longitude};{data.latitude},{data.longitude}?overview=false"
    res = requests.get(url).json()

    duree_sec = res['routes'][0]['duration']
    print(f"----------\nTemps de trajet: {duree_sec/3600.2f} heures")