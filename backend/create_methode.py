import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

"""
Generation d'un memoire technique PDF a partir des donnees frontend et des Q/R.
Le nom historique "fill_memoire_docx" est conserve pour compatibilite.
"""


quality_demarche = """
Depuis 2022 ; l’Atelier d’architecture AdA et l’agence ALU font partie du groupe ALU-AdA. Ce
rapprochement entre les sociétés d’architecture ALU et AdA s’est fait naturellement grâce aux
valeurs communes qui actionnent la rigueur et le développement d’un acte de bâtir durable et
sociétal.
L’atelier d’architecture AdA bénéficie depuis 2004 de la certification « QUALITE » ISO 9001
(certification délivrée par l’AFAQ), n° QUAL / 2004 / 23576a. Le domaine de certification couvre
les activités de “Conception Architecturale et Direction de Chantier pour des opérations de
construction et d’aménagement”, c’est-à-dire l’ensemble des activités de maîtrise d’œuvre. ALU a
donc engagée la même démarche pour avec comme ambition l’extension de la certification de
AdA à ALU en 2026.
La démarche de gestion de la Qualité suivant la norme ISO 9001 est proposée au maître
d’Ouvrage pour cette opération. Elle porte sur l’ensemble de la mission, des études préliminaires
à l’année de parfait achèvement.
Cette démarche vise en particulier, conformément à l’article 1.1 de la norme ISO 9001, à :
- fournir un produit conforme aux exigences du client et aux exigences réglementaires
applicables,
- accroître la satisfaction du client, par une application efficace du système et son amélioration
continue.
Le PLAN QUALITE met en œuvre des méthodes de travail et des procédures de contrôle très
élaborées, qui permettent de garantir le résultat de la mission sur les bases attendues par l’AFAQ
pour la certification ISO 9001.
A chaque étape de la mission, le projet est évalué sur la base des critères d’appréciation suivants
:
− Respect du programme,
− Respect du budget et du cout de construction,
− Respect de la règlementation et du cadre légal en vigueur,
− Respect des délais de réalisation des prestations,
− Ecoute du client et des usagers."""


def _to_str(value) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _normalize(text: str) -> str:
    return "".join(ch for ch in _to_str(text).lower() if ch.isalnum() or ch.isspace()).strip()


def _is_implication_section_title(title: str) -> bool:
    """
    Détecte la section d'implication même si le front envoie
    des variantes (numérotation, apostrophes, singulier/pluriel).
    """
    t = _normalize(title)
    return (
        ("implication" in t or "implications" in t)
        and "membres" in t
        and "mission" in t
    )


def _get_answer(qr_list, contains: str, default: str = "Information non precisee") -> str:
    needle = contains.lower()
    for item in qr_list or []:
        q = _to_str(item.get("question", "")).lower()
        if needle in q:
            rep = _to_str(item.get("reponse", ""))
            if rep:
                return rep
    return default


def _extract_sections_from_chapters(payload: dict) -> list[dict]:
    chapters = payload.get("chapters")
    if not isinstance(chapters, list):
        return []
    sections = []
    for ch in chapters:
        if not isinstance(ch, dict):
            continue
        for sec in ch.get("sections", []) if isinstance(ch.get("sections"), list) else []:
            if isinstance(sec, dict):
                sections.append(sec)
    return sections


def _extract_moyens_humains_sections(payload: dict) -> list[dict]:
    """
    Normalise les donnees de moyens humains provenant du frontend.
    Accepte plusieurs formes (administrations, team, moyensHumains).
    """
    sections = []

    administrations = payload.get("administrations")
    if not isinstance(administrations, list):
        # Donnees front actuelles: administrations imbriquees dans chapters[].sections[]
        administrations = []
        for sec in _extract_sections_from_chapters(payload):
            sec_title = _normalize(sec.get("title", ""))
            if "moyens humains affect" not in sec_title:
                continue
            if isinstance(sec.get("administrations"), list):
                administrations.extend(sec.get("administrations"))

    if isinstance(administrations, list):
        for item in administrations:
            if not isinstance(item, dict):
                continue
            membres = item.get("moyensHumains")
            if not isinstance(membres, list):
                membres = item.get("intervenants")
            members = []
            if isinstance(membres, list):
                for mh in membres:
                    if not isinstance(mh, dict):
                        continue
                    nom = _to_str(mh.get("nom") or mh.get("name"))
                    desc = _to_str(mh.get("description") or mh.get("role") or mh.get("mission"))
                    if nom or desc:
                        members.append({"nom": nom, "description": desc})

            sections.append(
                {
                    "id": _to_str(item.get("id")),
                    "name": _to_str(item.get("name") or item.get("administrationName") or item.get("entite")),
                    "description": _to_str(item.get("description")),
                    "competences": item.get("competences") if isinstance(item.get("competences"), list) else [],
                    "role_phase_etudes": _to_str(item.get("rolePhaseEtudes") or item.get("role_phase_etudes")),
                    "role_phase_chantier": _to_str(item.get("rolePhaseChantier") or item.get("role_phase_chantier")),
                    "members": members,
                }
            )

    if sections:
        return sections

    # Fallback minimal: une liste plate de moyens humains
    flat_members = payload.get("moyensHumains")
    if isinstance(flat_members, list):
        members = []
        for mh in flat_members:
            if not isinstance(mh, dict):
                continue
            nom = _to_str(mh.get("nom") or mh.get("name"))
            desc = _to_str(mh.get("description") or mh.get("role") or mh.get("mission"))
            if nom or desc:
                members.append({"nom": nom, "description": desc})
        if members:
            return [
                {
                    "id": _to_str(payload.get("group_id")),
                    "name": _to_str(payload.get("group_label")) or "Equipe de maitrise d'oeuvre",
                    "description": "",
                    "competences": [],
                    "role_phase_etudes": "",
                    "role_phase_chantier": "",
                    "members": members,
                }
            ]

    return []


def _extract_moyens_administrations_from_chapters(payload: dict) -> list[dict]:
    administrations = []
    for sec in _extract_sections_from_chapters(payload):
        sec_title = _normalize(sec.get("title", ""))
        if "moyens humains affect" not in sec_title:
            continue
        sec_admins = sec.get("administrations")
        if isinstance(sec_admins, list):
            administrations.extend([a for a in sec_admins if isinstance(a, dict)])
    return administrations


def _extract_competence_grid(payload: dict, moyens_sections: list[dict]) -> dict:
    """
    Normalise une grille de competences (matrice mission x entite).
    Format attendu prefere:
    {
      "headers": ["ALU", "LOIZILLON", "LBE", "CDUBETON"],
      "rows": [{"mission":"ESQUISSE","values":["C+E","", "E","E"]}, ...]
    }
    """
    raw = payload.get("competenceGrid")
    if not isinstance(raw, dict):
        raw = payload.get("implicationGrid")
    if not isinstance(raw, dict):
        raw = payload.get("grilleCompetences")

    if isinstance(raw, dict):
        headers = raw.get("headers")
        rows = raw.get("rows")
        if isinstance(headers, list) and isinstance(rows, list):
            clean_headers = [_to_str(h) for h in headers if _to_str(h)]
            clean_rows = []
            for r in rows:
                if not isinstance(r, dict):
                    continue
                mission = _to_str(r.get("mission") or r.get("phase") or r.get("label"))
                values = r.get("values")
                if not isinstance(values, list):
                    values = []
                clean_rows.append({"mission": mission, "values": [_to_str(v) for v in values]})
            if clean_headers and clean_rows:
                return {"headers": clean_headers, "rows": clean_rows}

    # Donnees front actuelles: implicationMatrix dans chapters[].sections[]
    for sec in _extract_sections_from_chapters(payload):
        sec_title = _to_str(sec.get("title", ""))
        if not _is_implication_section_title(sec_title):
            continue
        administrations = sec.get("administrations") if isinstance(sec.get("administrations"), list) else []
        if not administrations:
            # Le front renseigne parfois uniquement implicationMatrix dans cette section.
            # On récupère alors les administrations depuis la section "Moyens humains".
            administrations = _extract_moyens_administrations_from_chapters(payload)
        headers = [_to_str(a.get("name")) for a in administrations if isinstance(a, dict) and _to_str(a.get("name"))]
        matrix = sec.get("implicationMatrix") if isinstance(sec.get("implicationMatrix"), list) else []
        rows = []
        for row in matrix:
            if not isinstance(row, dict):
                continue
            label = _to_str(row.get("label"))
            values_by_admin = row.get("valuesByAdmin") if isinstance(row.get("valuesByAdmin"), dict) else {}
            values = []
            for admin in administrations:
                if not isinstance(admin, dict):
                    values.append("")
                    continue
                admin_key = str(admin.get("id", ""))
                cell_vals = values_by_admin.get(admin_key, [])
                if isinstance(cell_vals, list):
                    values.append(" + ".join(_to_str(v) for v in cell_vals if _to_str(v)))
                else:
                    values.append("")
            rows.append({"mission": label, "values": values})
        if headers and rows:
            return {"headers": headers, "rows": rows}

    headers = []
    for s in moyens_sections:
        name = _to_str(s.get("name"))
        if name:
            headers.append(name)
    if not headers:
        headers = ["Entite 1", "Entite 2", "Entite 3", "Entite 4"]

    default_rows = [
        {"mission": "ESQUISSE", "values": ["C+E"] + ["E"] * (len(headers) - 1)},
        {"mission": "AVP", "values": ["C+E"] + ["E"] * (len(headers) - 1)},
        {"mission": "PRO", "values": ["C+E"] + ["E"] * (len(headers) - 1)},
        {"mission": "DCE", "values": ["C+E"] + ["P"] * (len(headers) - 1)},
        {"mission": "ANALYSE DES OFFRES", "values": ["C+E"] + ["P"] * (len(headers) - 1)},
        {"mission": "DET SUIVI DE CHANTIER", "values": ["C+E"] + ["P"] * (len(headers) - 1)},
        {"mission": "AOR / DOE", "values": ["C+E"] + ["P"] * (len(headers) - 1)},
    ]
    return {"headers": headers, "rows": default_rows}


def create_memoire_payload(body: dict, qr_list: list[dict] | None = None) -> dict:
    payload = body if isinstance(body, dict) else {}
    qrs = qr_list if isinstance(qr_list, list) else []
    moyens_sections = _extract_moyens_humains_sections(payload)
    return {
        "title": _to_str(payload.get("title")) or "MEMOIRE TECHNIQUE DU GROUPEMENT DE MAITRISE D'OEUVRE",
        "group_label": _to_str(payload.get("group_label")) or "ALU - LBEI - CduBeton",
        "project_title": _to_str(payload.get("project_title"))
        or _get_answer(qrs, "type d'operation", "REHABILITATION D'UN EQUIPEMENT PUBLIC"),
        "intro": payload.get("intro")
        if isinstance(payload.get("intro"), list)
        else [
            "L'objet de la presente note est de montrer au maitre d'ouvrage la maniere dont l'equipe s'organise pour mener a bien le projet.",
            "L'enthousiasme, le professionnalisme et la proximite des membres de l'equipe sont les garants de son implication.",
            "Le groupement est fonde sur la complementarite et mobilise les moyens necessaires en etudes comme en chantier.",
        ],
        "phases": payload.get("phases")
        if isinstance(payload.get("phases"), list)
        else [
            {"phase": "ESQ", "livrables": "Note de presentation + plans d'esquisse + estimation sommaire", "delai": "2 semaines"},
            {"phase": "AVP", "livrables": "Notice + plans AVP + estimation detaillee + calendrier", "delai": "8 semaines"},
            {"phase": "PRO", "livrables": "Plans projet + CCTP + planning d'execution", "delai": "8 semaines"},
            {"phase": "DCE", "livrables": "Dossier de consultation + DPGF + plans", "delai": "2 semaines"},
            {"phase": "ACT/DET/AOR", "livrables": "Analyse des offres + suivi chantier + reception", "delai": "Selon operation"},
        ],
        "moyens_humains_sections": moyens_sections,
        "competence_grid": _extract_competence_grid(payload, moyens_sections),
        "qr_list": qrs,
    }


def fill_memoire_docx(payload: dict) -> str:
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "memoire_technique.pdf")

    styles = getSampleStyleSheet()
    # Palette du document de reference MEMOIRE TECH_ALU.pdf
    COLOR_TITLE = colors.HexColor("#ED7D31")
    COLOR_ACCENT = colors.HexColor("#FF6600")
    title_style = ParagraphStyle(
        "MemoTitle",
        parent=styles["Heading1"],
        textColor=COLOR_TITLE,
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        alignment=TA_CENTER,
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "MemoSubTitle",
        parent=styles["Heading2"],
        textColor=colors.black,
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=13,
        alignment=TA_CENTER,
        spaceAfter=2,
    )
    h2_style = ParagraphStyle(
        "MemoH2",
        parent=styles["Heading2"],
        textColor=colors.black,
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=12.5,
        alignment=TA_LEFT,
        spaceBefore=12,
        spaceAfter=6,
    )
    h2_main_style = ParagraphStyle(
        "MemoH2Main",
        parent=h2_style,
        spaceBefore=0,
        spaceAfter=0,
    )
    h3_style = ParagraphStyle(
        "MemoH3",
        parent=styles["Normal"],
        textColor=colors.black,
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=12,
        alignment=TA_LEFT,
        spaceBefore=6,
        spaceAfter=3,
    )
    label_style = ParagraphStyle(
        "MemoLabel",
        parent=styles["Normal"],
        textColor=colors.black,
        fontName="Helvetica",
        fontSize=10,
        leading=12,
        spaceBefore=5,
        spaceAfter=3,
    )
    accent_style = ParagraphStyle(
        "MemoAccent",
        parent=styles["Normal"],
        textColor=COLOR_ACCENT,
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=12,
        spaceAfter=3,
    )
    normal_style = ParagraphStyle(
        "MemoNormal",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=12,
        spaceAfter=3,
    )
    bullet_style = ParagraphStyle(
        "MemoBullet",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=12,
        leftIndent=12,
        spaceAfter=2,
    )

    doc = SimpleDocTemplate(
        out_path,
        pagesize=A4,
        rightMargin=1.8 * cm,
        leftMargin=1.8 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.8 * cm,
    )

    intro_blocks = payload.get("intro") if isinstance(payload.get("intro"), list) else []
    phases = payload.get("phases") if isinstance(payload.get("phases"), list) else []
    moyens_sections = payload.get("moyens_humains_sections") if isinstance(payload.get("moyens_humains_sections"), list) else []
    competence_grid = payload.get("competence_grid") if isinstance(payload.get("competence_grid"), dict) else {}
    qr_list = payload.get("qr_list") if isinstance(payload.get("qr_list"), list) else []

    def add_main_section_heading(elements_list: list, title: str) -> None:
        elements_list.append(Spacer(1, 4))
        elements_list.append(
            HRFlowable(
                width="100%",
                thickness=0.4,
                color=colors.HexColor("#222222"),
                spaceBefore=0,
                spaceAfter=2,
            )
        )
        elements_list.append(Paragraph(title, h2_main_style))
        elements_list.append(
            HRFlowable(
                width="100%",
                thickness=0.4,
                color=colors.HexColor("#222222"),
                spaceBefore=1,
                spaceAfter=4,
            )
        )

    elements = [
        Paragraph(_to_str(payload.get("title")), title_style),
        Paragraph(_to_str(payload.get("group_label")), subtitle_style),
        Paragraph(_to_str(payload.get("project_title")), subtitle_style),
        Spacer(1, 10),
    ]

    for txt in intro_blocks:
        intro_text = _to_str(txt)
        if intro_text.lower().startswith("l'enthousiasme") or intro_text.lower().startswith("l’enthousiasme"):
            elements.append(Paragraph(intro_text, accent_style))
        else:
            elements.append(Paragraph(intro_text, normal_style))
        elements.append(Spacer(1, 3))

    add_main_section_heading(elements, "NOTRE PHILOSOPHIE ET MOTIVATION")

    add_main_section_heading(elements, "METHODOLOGIE ET ORGANISATION")
    elements.extend([Paragraph("I. Livrables et delais de realisation des prestations par phase", h3_style), Spacer(1, 8)])

    table_data = [["Phase", "Livrables", "Delais"]]
    for p in phases:
        table_data.append(
            [
                _to_str(p.get("phase", "")),
                _to_str(p.get("livrables", "")),
                _to_str(p.get("delai", "")),
            ]
        )
    phases_table = Table(table_data, colWidths=[2.4 * cm, 11.2 * cm, 3.4 * cm], repeatRows=1)
    phases_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#efefef")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    elements.append(phases_table)

    elements.append(Spacer(1, 14))
    add_main_section_heading(elements, "II. Moyens humains affectes au projet")

    if moyens_sections:
        for section in moyens_sections:
            section_name = _to_str(section.get("name")) or "Entite"
            elements.append(Paragraph(section_name, h3_style))

            section_desc = _to_str(section.get("description"))
            if section_desc:
                elements.append(Paragraph(section_desc, normal_style))

            competences = section.get("competences") if isinstance(section.get("competences"), list) else []
            if competences:
                elements.append(Paragraph("Competences en :", accent_style))
                for comp in competences:
                    comp_text = _to_str(comp)
                    if comp_text:
                        elements.append(Paragraph(f"- {comp_text}", accent_style))

            members = section.get("members") if isinstance(section.get("members"), list) else []
            if members:
                elements.append(Paragraph("LES INTERVENANTS DEDIES A L'EXECUTION DU MARCHE :", accent_style))
                for member in members:
                    nom = _to_str(member.get("nom"))
                    desc = _to_str(member.get("description"))
                    if nom and desc:
                        elements.append(Paragraph(f"- <b>{nom}</b> : {desc}", bullet_style))
                    elif nom:
                        elements.append(Paragraph(f"- <b>{nom}</b>", bullet_style))
                    elif desc:
                        elements.append(Paragraph(f"- {desc}", bullet_style))

            role_etudes = _to_str(section.get("role_phase_etudes"))
            if role_etudes:
                elements.append(Paragraph("ROLE EN PHASE ETUDES :", accent_style))
                elements.append(Paragraph(role_etudes, normal_style))

            role_chantier = _to_str(section.get("role_phase_chantier"))
            if role_chantier:
                elements.append(Paragraph("ROLE EN PHASE CHANTIER :", accent_style))
                elements.append(Paragraph(role_chantier, normal_style))

            elements.append(Spacer(1, 12))
    else:
        elements.append(Paragraph("Aucun moyen humain detaille n'a ete transmis par le frontend.", normal_style))

    elements.append(Spacer(1, 8))
    add_main_section_heading(elements, "III. Implication des membres de l'equipe durant la mission")
    elements.append(
        Paragraph(
            "E : Execute la mission selon sa competence.<br/>"
            "P : Participe selon sa competence.<br/>"
            "C : Coordonne, realise compte rendu de reunion &amp; synthese de la phase",
            normal_style,
        )
    )

    grid_headers = competence_grid.get("headers") if isinstance(competence_grid.get("headers"), list) else []
    grid_rows = competence_grid.get("rows") if isinstance(competence_grid.get("rows"), list) else []
    if grid_headers and grid_rows:
        matrix_data = [["Mission"] + [_to_str(h) for h in grid_headers]]
        for row in grid_rows:
            if not isinstance(row, dict):
                continue
            mission = _to_str(row.get("mission") or "Mission")
            values = row.get("values") if isinstance(row.get("values"), list) else []
            values = [_to_str(v) for v in values]
            if len(values) < len(grid_headers):
                values.extend([""] * (len(grid_headers) - len(values)))
            elif len(values) > len(grid_headers):
                values = values[: len(grid_headers)]
            matrix_data.append([mission] + values)

        mission_col_width = 5.0 * cm
        remaining_width = 16.2 * cm - mission_col_width
        other_col_width = remaining_width / max(len(grid_headers), 1)
        col_widths = [mission_col_width] + [other_col_width] * len(grid_headers)

        grid_table = Table(matrix_data, colWidths=col_widths, repeatRows=1)
        grid_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#efefef")),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        elements.append(Spacer(1, 4))
        elements.append(grid_table)
    else:
        elements.append(Paragraph("Grille de competences non fournie.", normal_style))

    add_main_section_heading(elements, "ENVIRONNEMENT")
    elements.extend(
        [
            Spacer(1, 8),
            Paragraph(
                "L'enveloppe, interface active entre l'environnement extérieur et bâtiment, doit être pensée et "
                "conçue intelligemment, pour en tirer l'essentiel de ses ressources, et maximiser ses capacités. "
                "Elle est aussi le lieu privilégié de rencontre entre le développement durable et l'architecture.",
                normal_style,
            ),
            Paragraph(
                "Elément central de la qualité du bâtiment, première clé de réflexion pour le confort et partie la "
                "plus durable de la construction, elle sera notre préoccupation prioritaire.",
                normal_style,
            ),
            Paragraph(
                "S'agissant d'un bâtiment existant, dans lesquels l'intervention se fera dans le périmètre actuel, "
                "les performances environnementales porteront sur les thèmes suivants :",
                normal_style,
            ),
            Paragraph("1. Sobriété énergétique et performance", h3_style),
            Paragraph(
                "Le projet privilégiera une démarche de sobriété énergétique fondée sur la réduction des besoins "
                "avant recours aux systèmes techniques.",
                normal_style,
            ),
            Paragraph("Les principes retenus sont :", normal_style),
            Paragraph("− Optimisation de l'enveloppe existante (isolation thermique, menuiseries performantes)", bullet_style),
            Paragraph("− Valorisation des apports naturels (éclairage naturel, apports solaires passifs)", bullet_style),
            Paragraph("− Mise en œuvre d'équipements sobres (éclairage LED, régulation, ventilation performante)", bullet_style),
            Paragraph("− Recours à des systèmes énergétiques à haut rendement, adaptés au bâtiment", bullet_style),
            Paragraph(
                "Cette approche vise une réduction durable des consommations et des coûts d'exploitation.",
                normal_style,
            ),
            Paragraph("2. Compatibilité patrimoniale", h3_style),
            Paragraph("Les interventions seront conçues dans le respect du bâti existant :", normal_style),
            Paragraph("− Préservation des caractéristiques architecturales", bullet_style),
            Paragraph("− Choix de solutions réversibles et non invasives", bullet_style),
            Paragraph("− Intégration discrète des équipements techniques", bullet_style),
            Paragraph(
                "Les matériaux et techniques sont adaptés aux contraintes du bâti ancien (gestion hygrothermique, "
                "compatibilité des supports), garantissant un équilibre entre performance et conservation patrimoniale.",
                normal_style,
            ),
            Paragraph("3. Matériaux à faible impact", h3_style),
            Paragraph("Le projet privilégiera des matériaux :", normal_style),
            Paragraph("− À faible empreinte carbone (biosourcés, géosourcés)", bullet_style),
            Paragraph("− Disposant de données environnementales vérifiées (FDES/ACV)", bullet_style),
            Paragraph("− Issus de filières locales lorsque possible", bullet_style),
            Paragraph("− Faiblement émissifs pour garantir la qualité de l'air intérieur", bullet_style),
            Paragraph(
                "Ces choix contribuent à la réduction de l'impact environnemental global de l'opération.",
                normal_style,
            ),
            Paragraph("4. Réemploi et gestion des déchets", h3_style),
            Paragraph("Une démarche d'économie circulaire pourra être mise en œuvre :", normal_style),
            Paragraph("− Réalisation d'un diagnostic ressources", bullet_style),
            Paragraph("− Priorité au réemploi in situ des éléments existants", bullet_style),
            Paragraph("− Orientation vers des filières de réemploi externes", bullet_style),
            Paragraph(
                "La gestion des déchets de chantier comprend : le tri à la source, la traçabilité des flux, la valorisation.",
                normal_style,
            ),
            Paragraph("5. Chantier à nuisances réduites", h3_style),
            Paragraph("L'organisation du chantier intégrera :", normal_style),
            Paragraph("− Limitation des nuisances sonores et des poussières", bullet_style),
            Paragraph("− Limitation des nuisances visuelles", bullet_style),
            Paragraph("− Gestion optimisée des flux et des livraisons", bullet_style),
            Paragraph("− Utilisation d'équipements à faibles émissions", bullet_style),
            Paragraph("6. Prise en compte du décret tertiaire", h3_style),
            Paragraph(
                "Le projet s'inscrira dans le respect de la trajectoire du décret tertiaire :",
                normal_style,
            ),
            Paragraph("− Réduction des consommations énergétiques", bullet_style),
            Paragraph("− Intégration de dispositifs de suivi (comptage, GTB)", bullet_style),
            Paragraph("− Optimisation de l'exploitation et de la maintenance", bullet_style),
            Spacer(1, 14),
        ]
    )

    if qr_list:
        add_main_section_heading(elements, "ANNEXE - Questions / Reponses issues de l'analyse")
        for i, qa in enumerate(qr_list, start=1):
            q = _to_str(qa.get("question", f"Question {i}"))
            r = _to_str(qa.get("reponse", "Information non precisee"))
            elements.append(Paragraph(f"<b>Q{i}. {q}</b>", normal_style))
            elements.append(Paragraph(r, normal_style))
            elements.append(Spacer(1, 6))
    else:
        add_main_section_heading(elements, "ANNEXE - Questions / Reponses issues de l'analyse")
        elements.append(Paragraph("Aucune question/reponse disponible.", normal_style))

    doc.build(elements)
    return out_path





