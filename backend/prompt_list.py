import os


# REFERENCE = """

# # Nouveau prompt "REFERENCE" (utilisé par le backend)
# Tu es un extracteur strict.
# Ta mission : extraire, depuis le CONTEXTE, les informations relatives aux références exigées dans l'appel d'offres.

# CONTRAINTES DE SORTIE (STRICTES) :
# 1) Réponds EXCLUSIVEMENT avec un JSON valide et rien d'autre (aucun texte avant/après, aucune balise Markdown, aucun commentaire).
# 2) Le JSON doit être un tableau (liste) d'objets.
# 3) Si aucune information de références n'est trouvée : renvoie `[]`.
# 4) Si une information de champ manque pour un objet donné : renvoie `null` pour ce champ.

# STRUCTURE DE SORTIE :
# [
#   {
#     "catégorie": string | null,
#     "nombre_références": number | null,
#     "nature_operation": "Réhabilitation" | "Neuve" | "Extension" | "Rénovation thermique" | null,
#     "site_occupe": true | false | null,
#     "surface_SDP_minimum": number | null,
#     "type_infrastructure": "Logements" | "Sportif" | "Résidence" | "Tertiaire" | "Scolaire" | "Commerce" | null,
#     "anciennete_max_projet": number | null
#   }
# ]

# RÈGLES D'INTERPRÉTATION :
# - nature_operation :
#   - "Réhabilitation" si le contexte parle de : réhabilitation, rénovation, restructuration, réhabilités
#   - "Neuve" si le contexte parle de : neuf, construction, création
#   - "Extension" si le contexte parle de : extension, agrandissement
#   - "Rénovation thermique" si le contexte parle de : énergétique, thermique, CRE, MGP
# - type_infrastructure :
#   - "Scolaire" si : collège, lycée, école, enseignement (et assimilés)
#   - "Commerce" si : restaurant, magasin, boutique
#   - "Sportif" si : gymnase, stade, terrain
#   - "Logements" si : appartement, habitat, immeuble
#   - "Tertiaire" si : bureaux, administration, équipement public administratif
#   - "Résidence" si : résidence
# - site_occupe :
#   - true si le contexte indique explicitement un site occupé / établissement en fonctionnement / milieu habité
#   - false si le contexte indique explicitement l'absence de site occupé
#   - sinon null
# - surface_SDP_minimum :
#   - extraire uniquement le nombre X quand le contexte exprime une SDP avec un seuil (ex: "SDP >= X m²", "supérieure ou égale à X m²", "au moins X m²").
# - anciennete_max_projet :
#   - extraire X quand le contexte indique "sur les X dernières années" / "dans les X dernières années"
# - nombre_références :
#   - extraire le nombre X quand le contexte demande "X références" / "X références réalisées" (par catégorie si plusieurs blocs distincts apparaissent).

# GESTION DES CAS MULTIPLES :
# - Si plusieurs blocs distincts de références sont présents, renvoie plusieurs objets dans le tableau (un par bloc).
# - Si plusieurs valeurs valides existent pour un champ dans un même bloc, prends la première valeur valide qui apparaît dans le contexte.
# - Ne recopie pas le texte source : utilise uniquement les valeurs normalisées (listes autorisées) pour nature_operation et type_infrastructure.

# RAPPEL STRICT :
# Ne renvoie que le JSON (un tableau), jamais de texte autour.
# """


# REFERENCE = """

# Tu es un extracteur strict de références de projets à partir d’un texte de contexte.
# Ta mission : extraire toutes les informations de références demandées dans l'appel d'offres selon la structure donnée.

# CONTRAINTES STRICTES :
# Répond uniquement avec un JSON valide, rien d’autre (pas de texte, balises ou commentaires).
# Le JSON doit être un tableau d’objets.
# Si aucune info n’est trouvée, renvoie [].
# Si un champ est manquant pour un objet, mets null.
# STRUCTURE JSON :

# [
# {
# "catégorie": string | null,
# "nombre_références": number | null,
# "nature_operation": "Réhabilitation" | "Neuve" | "Extension" | "Rénovation thermique" | null,
# "site_occupe": true | false | null,
# "surface_SDP_minimum": number | null,
# "type_infrastructure": "Logements" | "Sportif" | "Résidence" | "Tertiaire" | "Scolaire" | "Commerce" | null,
# "anciennete_max_projet": number | null
# }
# ]

# RÈGLES D’INTERPRÉTATION :
# nature_operation :
# "Réhabilitation" si le texte parle de réhabilitation, rénovation, restructuration, réhabilités
# "Neuve" si le texte parle de neuf, construction, création
# "Extension" si le texte parle de extension, agrandissement
# "Rénovation thermique" si le texte parle de énergétique, thermique, CRE, MGP
# type_infrastructure :
# "Scolaire" si collège, lycée, école, enseignement
# "Commerce" si restaurant, magasin, boutique
# "Sportif" si gymnase, stade, terrain
# "Logements" si appartement, habitat, immeuble
# "Tertiaire" si bureaux, administration, équipement public administratif
# "Résidence" si résidence
# site_occupe :
# true si le texte indique site occupé / établissement en fonctionnement / milieu habité
# false si le texte indique explicitement absence de site occupé
# sinon null
# surface_SDP_minimum : extraire le nombre si le texte indique SDP avec seuil (ex: "SDP ≥ X m²", "au moins X m²")
# anciennete_max_projet : extraire le nombre si le texte mentionne "dans les X dernières années"
# nombre_références : extraire le nombre si le texte indique "X références" ou "X références réalisées"
# GESTION DES CAS MULTIPLES :
# Si plusieurs blocs distincts de références existent, crée un objet par bloc.
# Si plusieurs valeurs pour un même champ, prends la première valide.
# Normalise les valeurs selon les listes autorisées pour nature_operation et type_infrastructure.
# RÈGLE FINALE :
# Ne renvoie que le JSON, jamais de texte autour.

# """
SYSTEM = """
Tu es un assistant spécialisé dans l'analyse d'appels d'offres et de marchés publics.
Tu extrais uniquement des informations factuelles présentes dans le contexte (texte du document fourni ci-dessous).

Règles de fond :
- N'INVENTE JAMAIS AUCUNE INFORMATION.
- Ne cite JAMAIS d'article, extraits les informations.
- S'il y a plusieurs questions, réponds uniquement à celles dont la réponse figure dans le texte fourni ; ignore les autres. Donne une réponse par question, sans préfixe ("Réponse :", "La réponse est :", etc.).
- Si l'information n'est pas renseignée dans le texte fourni, réponds uniquement : "Information non précisée".
- Chiffres, montants, numéros de téléphones et dates : restitue-les tels qu'ils apparaissent (unités, symboles €, format) sans reformuler ni approximer.
- En cas d'ambiguïté, donne la réponse la plus cohérente avec le contexte, sans inventer.

Format de réponse :
- Réponse courte et factuelle.
- Pas d'explication ni de phrase d'introduction.
- Réponds uniquement par la réponse attendue, sans formule ni commentaire.
"""

REFERENCE = """
Tu es un extracteur strict d'informations de références de projets à partir d’un texte de contexte.

Ta mission : extraire toutes les informations relatives aux références demandées dans un appel d'offres selon la structure donnée.

### CONTRAINTES STRICTES :
1) Répond uniquement avec un JSON valide, rien d’autre (pas de texte, balises ou commentaires).  
2) Le JSON doit être un tableau d’objets.  
3) Si aucune information n’est trouvée pour un champ, mets `null`.  
4) Si aucune référence n’est trouvée dans le contexte, renvoie `[]`.  
5) **Priorité : remplir `catégorie`, `type_infrastructure` et `anciennete_max_projet` si elles sont explicitement mentionnées.**
6) Si aucune information n'est trouvé pour remplir le JSON renvoie "Aucune information trouvée" sans rien d'autre

### STRUCTURE JSON :
[
  {
    "catégorie": string | null,
    "nombre_références": number | null,
    "nature_operation": "Réhabilitation" | "Neuve" | "Extension" | "Rénovation thermique" | null,
    "site_occupe": true | false | null,
    "surface_SDP_minimum": number | null,
    "type_infrastructure": "Logements" | "Sportif" | "Résidence" | "Tertiaire" | "Scolaire" | "Commerce" | null,
    "anciennete_max_projet": number | null
  }
]

### RÈGLES D’INTERPRÉTATION :
- **nature_operation** :
  - "Réhabilitation" si le texte parle de réhabilitation, rénovation, restructuration, réhabilités  
  - "Neuve" si le texte parle de neuf, construction, création  
  - "Extension" si le texte parle de extension, agrandissement  
  - "Rénovation thermique" si le texte parle de énergétique, thermique, CRE, MGP  

- **type_infrastructure** :
  - "Scolaire" si collège, lycée, école, enseignement  
  - "Commerce" si restaurant, magasin, boutique  
  - "Sportif" si gymnase, stade, terrain  
  - "Logements" si appartement, habitat, immeuble  
  - "Tertiaire" si bureaux, administration, équipement public administratif  
  - "Résidence" si résidence  

- **site_occupe** :
  - true si le texte indique explicitement site occupé / établissement en fonctionnement / milieu habité  
  - false si le texte indique explicitement absence de site occupé  
  - sinon null  

- **surface_SDP_minimum** :
  - extraire uniquement le nombre si le texte exprime une SDP minimale (ex : "SDP ≥ X m²", "au moins X m²")  

- **anciennete_max_projet** :
  - extraire le nombre si le texte mentionne "dans les X dernières années" ou "sur les X dernières années"  

- **nombre_références** :
  - extraire le nombre si le texte indique "X références" ou "X références réalisées"  

### GESTION DES CAS MULTIPLES :
- Si plusieurs blocs distincts de références existent, crée un objet par bloc.  
- Si plusieurs valeurs pour un même champ sont présentes, prends la première valeur valide.  
- Normalise toutes les valeurs selon les listes autorisées pour **nature_operation** et **type_infrastructure**.  

### EXEMPLE D’ENTRÉE → SORTIE JSON :

Contexte : 
"Dossier de référence sur 5 dernières années : 
- Catégorie 1 : 5 références de collèges et écoles neuves ou réhabilitées.
- Catégorie 2 : 5 références en conception-réalisation avec suivi d'exploitation-maintenance.
- Catégorie 3 : 5 références de réhabilitation sur site occupé.
- Catégorie 4 : 5 références de bâtiments réhabilités avec performances énergétiques.
- Catégorie 5 : 5 références de bâtiments réhabilités avec confort d’été.
- Catégorie 6 : 5 références de bâtiments réhabilités avec respect de la qualité de l’air intérieur."

Sortie JSON attendue :
[
  {
    "catégorie": "1",
    "nombre_références": 5,
    "nature_operation": null,
    "site_occupe": null,
    "surface_SDP_minimum": null,
    "type_infrastructure": "Scolaire",
    "anciennete_max_projet": 5
  },
  {
    "catégorie": "2",
    "nombre_références": 5,
    "nature_operation": null,
    "site_occupe": null,
    "surface_SDP_minimum": null,
    "type_infrastructure": null,
    "anciennete_max_projet": 5
  },
  {
    "catégorie": "3",
    "nombre_références": 5,
    "nature_operation": "Réhabilitation",
    "site_occupe": true,
    "surface_SDP_minimum": null,
    "type_infrastructure": null,
    "anciennete_max_projet": 5
  },
  {
    "catégorie": "4",
    "nombre_références": 5,
    "nature_operation": "Réhabilitation",
    "site_occupe": null,
    "surface_SDP_minimum": null,
    "type_infrastructure": null,
    "anciennete_max_projet": 5
  },
  {
    "catégorie": "5",
    "nombre_références": 5,
    "nature_operation": "Réhabilitation",
    "site_occupe": null,
    "surface_SDP_minimum": null,
    "type_infrastructure": null,
    "anciennete_max_projet": 5
  },
  {
    "catégorie": "6",
    "nombre_références": 5,
    "nature_operation": "Réhabilitation",
    "site_occupe": null,
    "surface_SDP_minimum": null,
    "type_infrastructure": null,
    "anciennete_max_projet": 5
  }
]

### RÈGLE FINALE :
- Ne renvoie que le JSON, jamais de texte autour.
"""

VILLE = """
Tu es un extracteur strict.
Ta tâche est d’extraire UNE entité de type VILLE.

Règles ABSOLUES :
- La réponse doit contenir exactement un seul mot ou groupe de mots.
- Ce mot doit être UNIQUEMENT le nom de la ville (ex: "Lyon", "Saint-Denis").
- Il est INTERDIT d’inclure un code postal, un département, une région ou un pays.
- Il est INTERDIT d’ajouter des commentaires, phrases ou explications.
- Si aucune ville n’est clairement mentionnée, réponds exactement : Non précisé
- Ne donne aucun contexte."""


NOTE = """ 
Tu es un assistant spécialisé dans l'extraction d'informations de la note méthodologique d'un appel d'offres.
Sers toi du texte donner pour creer une liste de chapitres en puisant dans les elements suivants :
Tu dois imperativement garder l'ordre de citation pour la creation des chapitres.

Elements :
- Methodologie et organisation
- Compréhension du programme 
- Environnement
- References de la maitrise d'oeuvre
- Thematique sociale et organisationnelle

Exemple:
1. Methodologie et organisation
2. Compréhension du programme
3. Environnement
4. References de la maitrise d'oeuvre
5. Thematique sociale et organisationnelle

Format de réponse:
- Réponse courte et factuelle.
- Pas d'explication ni de phrase d'introduction.
- Réponds uniquement par la réponse attendue, sans formule ni commentaire.
"""

questions_rag = [
    {#1
        "llm": "Qu'est-ce qui est prévue pour ce projet? L'information est dans le header",
        "rerank": "Type de projet (école, gymnase, équipement culturel, bâtiment administratif)",
        "user": "Quel est le type d'infrastructure ?",
        "keyword": "Type"
    },
    {#2
        "llm": "Quelle est la nature de l’opération (construction neuve, extension, réhabilitation, rénovation, restructuration) ?",
        "rerank": "Nature du projet (neuf, extension, réhabilitation, rénovation, restructuration)",
        "user": "Quel est la nature de l'opération ?",
        "keyword" : "Nature"
    },
    {#3
        # "llm": "Donne moi le montant prévisionnel des travaux/projet indiqué dans le document ? Ou n'importe quel montant proposer par le document en echange de services. Explique a quoi sert le prix donner",
        "llm": "Analyse le document et indique le montant financier associé au projet (estimation, plafond, budget ou valeur du marché). Si plusieurs montants apparaissent, mentionne-les. Pour chaque montant, explique ce qu’il représente (limite maximale, coût prévu, montant contractuel, etc.) et à quoi il sert dans la consultation.",
        "rerank": "Montant/prix/cout prévisionnel du projet",
        "user": "Quel est le montant prévisionnel des travaux ?",
        "keyword" : "Travaux"
    },
    {#4
        "llm": "Dans quelle région administrative se situe le projet en te basant sur le texte fourni?",
        "rerank": "Région administrative du projet",
        "user": "Dans quelle région administratif se situe le projet ?",
        "keyword": "Region"
    },
    {#5
        "llm": "Extrait le(s) code(s) postal ou le(s) département(s) dans lequel se situe le projet",
        "rerank": "Dans quel code postal/département se trouve le projet",
        "user": "Dans quel département se situe le projet ?",
        "keyword": "Département"
    },
    {#6
        "llm": "Extrait uniquement le nom de la ville mentionnée dans le texte ci-dessous. Réponds uniquement par le nom de la ville, sans phrase, sans ponctuation, sans explication.S’il n’y a pas de ville clairement identifiable, réponds exactement par : AUCUNE.",
        "keyword": "Ville",
        "user": "Quelle est le nom de la ville ou se situe le projet?",
        "rerank": "Commune ou ville du projet"
    },
    {#7
        "llm": "Quelle est la succursale ou l’agence territoriale la plus proche mentionnée dans le document ?",
        "keyword": "Succursale",
        "user": "Quelle est la succursale ou l'agence territoriale la plus proche ?",
        "rerank": "Succursale ou agence territoriale la plus proche"
    },
    {#8
        "llm": "Qui est le maître d'ouvrage et quelles sont les informations que tu peux en extraire ? Si tu n'en as aucune répond juste avec le nom de maitre d'ouvrage",
        "keyword": "Ouvrage",
        "user": "Qui est le maitre d'ouvrages?",
        "rerank": "Maître d’ouvrage"
    },
    {#9
        "llm": "Extraits le numéro de telephone, l'adresse, l'adresse mail, le site web et le nom du mandataire dans ce format'Nom de la commune: Nom de la commune - Tél: numero de telephone OBLIGATOIREMENT a 10 chiffres - Représentant de l'acheteur: Nom du representant, site de l'acheteur: site - Adresse mail de l'acheteur: mail' et n'ajoute rien d'autres que ces infos, ne réponds pas si l'info n'est pas fournie. Il y aura surement les mots 'Affaire suivie par' a cote du nom",
        "keyword": "Mandataire",
        "user": "Qui est le mandataire du projet si il y en a un?",
        "rerank": "Mandataire du projet agissant pour le compte du maître d'ouvrage"
    },
    {#10
        "llm": "Quel est le type de sélection prévu (appel à candidatures ou appel d’offres) ?",
        "keyword": "Candidature",
        "user": "Quel est le type de sélection prévue?",
        "rerank": "Type de sélection (appel à candidatures / appel d’offres)"
    },
    {#11
        "llm": "Quel est le type de procédure de passation du marché (appel d’offres, concours, marché global de performance, procédure adaptée, etc.) ?",
        "keyword": "Procédure",
        "user": "Quel est le type de procédure de passation du marché ?",
        "rerank": "Type de procédure (AO, concours, MGP, etc.)"
    },
    {#12
        "llm": "Le document précise-t-il qu’un mandataire est requis ? Si oui, quel type de mandataire est demandé ?",
        "keyword": "Mandataire-requis",
        "user": "Qui est le mandataire requis et quel est son type si il y en a un",
        "rerank": "Mandataire requis et type"
    },
    {#13
        "llm": "Quelle est la date limite de remise des candidatures ou des offres (première échéance) ?",
        "keyword": "limite1", ##
        "user": "Quelle est la date limite de remise des candidatures ?",
        "rerank": "Quelle est la date limite de remise des candidatures"
    },
    {#14
        "llm": "Quelle est la date limite pour poser des questions ou demander des précisions auprès du maître d’ouvrage ?",
        "keyword": "Questions",
        "user": "Quelle est la date limite pour demander des renseignements supplémentaires?",
        "rerank": "Date limite pour questions"
    },
    {#15        
        "llm": "Quelle est la date limite de remise des offres ou des candidatures (seconde échéance), si elle est mentionnée ?",
        "user": "Quelle est la data limite de remises des candidatures (seconde échéance)?",
        "keyword": "Seconde échéance",
        "rerank": "Seconde échéance date limite de remise des candidatures"
    },
    {#16
        "llm": "Une exclusivité est-elle imposée aux bureaux d’études ? Si oui, sur combien d’équipes cette exclusivité s’applique-t-elle ?",
        "rerank": "Exclusivité bureaux d’études (oui/non) et nombre d’équipes",
        "user" : "Y a t il une exclusivité sur les bureaux d'études et sur combien d'équipes ?",
        # "rerank": "Le document prévoit-il une exclusivité imposée pour les bureaux d’études ?",
        "keyword": "Exclusivité"
    },
    {#17
        # "llm": "Une visite du site est-elle prévue ? Si oui, à quelle date ?",
        # "rerank": "Y a t-il un rendez-vous sur site ?",
        # "keyword": "Visite"
        "llm": "Le document mentionne-t-il une visite, une réunion ou un déplacement sur site prévu pour les candidats ou les participants ? Si oui à quelle date ?",
        "rerank": "Présence sur site, réunion ou visite organisée dans le cadre du projet ou du concours ?",
        "user" : "Est-ce qu'une visite du site est obligatoire?",
        "keyword": "Présence sur site"
    },
    {#18
        "llm": "Quelles sont les compétences ou spécialités exigées pour la constitution de l’équipe candidate ?",
        "rerank": "Compétences ou spécialités requises pour l’équipe",
        "user": "Quelles sont les compétences exigées pour la constitution de l'équipe ?",
        "keyword": "Compétences"
    },
    {#19
        "llm": "Combien de références professionnelles au total sont demandées au groupement dans le cadre de la candidature ? Detail en disant combien de references pqr cqtegorie et quel categorie si cela est possible",
        "rerank": "Combien de références sont demandées à l’architecte?",
        "user": "Combien de références minimum sont demandées a l'architecte?",
        "keyword": "Références"
    },
    {#20
        "llm": "Quelles sont les missions confiées au titulaire du marché (par exemple : mission complète, DIAG, FAISA, REL, EXE, etc.) ?",
        "rerank": "Missions demandées (mission complète, DIAG, FAISA, REL, EXE, etc.)",
        "user": "Quelles sont les missions demandées au titulaire du marché",
        "keyword": "Missions"
    },
    {#21
        "llm": "Le marché est-il découpé en tranches ? Si oui, combien de tranches sont prévues et quelles sont leurs natures (tranche ferme, tranche optionnelle) ?",
        "rerank": "Le marché est-il découpé en tranches (nombre et type : ferme / optionnelle)",
        "user": "Le marché est-il découpé en tranches? Si oui, lesquelles?",
        "keyword": "Tranches"
    },
    {#22
        "llm": "Quelles sont les phases de la mission, combien sont-elles et quelle est leur temporalité prévisionnelle ?",
        "rerank": "Phases de la mission (nombre et temporalité)",
        "user": "Quelles sont les phases de la mission?",
        "keyword": "Phases"
    },
    {#23
        # "llm": "Le projet prévoit-il l’intervention d’une AMO ou d’un MOD ? Si oui, lequel et par qui est-il assuré ?",
        # "rerank": "AMO ou MOD et entité concernée"
        "llm": "Le projet prévoit-il l’intervention d’une assistance à maîtrise d’ouvrage ou d’un maître d’ouvrage délégué ? Si oui, lequel et quelle entité en est responsable ?",
        "rerank": "Assistance à maîtrise d’ouvrage ou maîtrise d’ouvrage déléguée et entité responsable",
        "user": "Le projet prévoit il l'intervention d'une assistance a maitrise d'ouvrages?",
        "keyword": "Assistances"
    },
    {#24
        "llm": "Une prime de concours est-elle prévue ? Si oui, quel est le montant de cette prime ?",
        # "rerank": "Prime de concours (oui/non) et montant",
        "rerank": "Remise ou versement de prime avec montant",
        "user": "Une prime de concours est-elle prévue? Si oui, quel est son montant?",
        "keyword": "Prime"
    },
    {#25
        "llm": "Le document impose-t-il la réalisation d’une maquette (numérique ou physique) dans le cadre de la candidature ou de l’offre ?Si aucune information n'est fourni à ce sujet réponds seulement'Non précisé'",
        "rerank": "Maquette requise (oui/non)",
        "user": "La réalisation d'une maquette est elle imposé?",
        "keyword": "Maquette"
    },
    {#26
        "llm": "La réalisation d’un film de présentation est-elle exigée dans le cadre de la procédure ? Si aucune information n'est fourni à ce sujet réponds seulement'Non précisé'",
        "rerank": "Film requis (oui/non)",
        "user": "La réalisation d'un film est-elle imposée?",
        "keyword": "Film"
    },
    {#27                    
        "llm": "Un numéro de consultation se trouve probablment dans les extraits fournis. Extrais ce qui te semble être le numéro de consultation si rien n'y correspond répond 'Information non précisé'",
        "rerank": "Numéro de consultation ou d'appel d'offres",
        "user": "Quel est le numéro de consultation ou d'appel d'offres?",
        "keyword": "Numéro"
    },
    {#28
        "llm": "Quel est le type d'opération, sur quelle infrastructure et ou se situe l'infrastruscture en question ? Si tu ne trouves pas la réponses dans les extraits fournis répond 'Non précisé'",
        "rerank": "Type d'opération et infrastructure",
        "user": "Quel est le type d'opération et sur quelle infrastructure ?",
        "keyword": "Type d'opération"
    },
    {#29
        "llm": "Extraits toutes les informations concernant les références demandés",
        # "rerank": "Combien de références (capacités technique et experience) sont demandées et quelles sont leurs catégories ?",
        "rerank": "Quelles sont les expériences demandées ?",
        "user": "ref",
        "keyword": "Références"
    },
    {#30
        "llm": "Quels sont les critères d’appréciation ou d’évaluation mentionnés dans le texte et quels sont leurs pourcentages respectifs ?",
        "rerank": "Critères d’appréciation ou d’évaluation d’une offre avec pondération ou pourcentage (prix, valeur technique, délais).",
        "user": "Pourcentages",
        "keyword": "pourcentages"
    },
    {#31
        "llm": "?",
        "rerank": "Format de la note methodologique",
        "user": "Quels sont les points a prendre en compte pour la création de la note methodologique ?",
        "keyword": "Méthodologie"
    }
]