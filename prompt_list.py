import os

# REFERENCE= """
# Tu extrais les références demandées dans un appel d'offres.

# Règles :

# - Répond uniquement avec un JSON.
# - Ne copie jamais le texte.
# - Si l'information n'existe pas → null.
# - Si l'information existe mais n'a pas d'equivalent dans la liste fourni pour remplir le json, remplis avec "null"
# - Si le texte propose plusieurs options pour un champ, prends **uniquement le premier choix valide** selon la liste autorisée pour ce champ.

# Interdiction:
# - Toute valeur hors "Valeurs autorisées"

# Valeurs autorisées :

# nature_operation :
# Réhabilitation | Neuve | Extension | Rénovation thermique | null
# exemple:
# réhabilitation | rénovation | restructuration → Réhabilitation
# construction neuve → Neuve
# extension | agrandissement → Extension
# rénovation énergétique | rénovation thermique → Rénovation thermique

# type_infrastructure :
# Logements | Sportif | Résidence | Tertiaire | Scolaire | Commerce | null 
# exemple:
# collège, lycée, école = Scolaire
# restaurant, magasin, boutique = Commerce
# gymnase, terrain = Sprotif

# site_occupe :
# True | False | null

# Règles d'interprétation :

# Ancienneté
# "sur les X dernières années" → anciennete_max_projet = X

# Site occupé
# "site occupé" ou "établissement en fonctionnement" → site_occupe = True

# Infrastructure
# école | collège | lycée | enseignement → Scolaire

# Surface
# "SDP ≥ X m²" → surface_SDP_minimum = X

# Références
# "X références" → nombre_références = X

# Créer un objet JSON pour chaque catégorie.

# Format :
# [
# {
# "catégorie": string | null,
# "nombre_références": number | null,
# "nature_operation": "Réhabilitation" | "Neuve" | "Extension" | "Rénovation thermique" | null,
# "site_occupe": True | False | null,
# "surface_SDP_minimum": number | null,
# "type_infrastructure": "Logements" | "Sportif" | "Résidence" | "Tertiaire" | "Scolaire" | null,
# "anciennete_max_projet": number | null
# }
# ]

# Exemple :

# Texte :

# Présentation de 3 références réalisées (livrées) dans les 5 dernières années (condition sine qua non*) :
# - Référence n° 1 : Travaux de réhabilitation en site occupé d’une SDP supérieure ou égale à 4000 m².
# - Référence n° 2 : Travaux de réhabilitation d’un établissement d’enseignement secondaire ou
# supérieur ou ERP.
# - Référence n° 3 : Travaux de rénovation thermique (CRE ou MGP)
# Réponse :

# [
#   {
#     "catégorie": null,
#     "nombre_références": 3,
#     "nature_operation": "Réhabilitation | Réhabilitation | Rénovation thermique",
#     "site_occupe": "True | False | False",
#     "surface_SDP_minimum": "4000 | null | null",
#     "type_infrastructure": "null | Scolaire | null",
#     "anciennete_max_projet": 5
#   }
# ]
# """


REFERENCE = """
## INSTRUCTIONS D'EXTRACTION
Tu es un expert en analyse d'appels d'offres. Ton rôle est d'extraire les critères de références demandés sous forme de JSON strict.

### RÈGLES CRITIQUES :
1. NE JAMAIS RECOPIER le texte source. Si le texte dit "collèges", tu écris "Scolaire".
2. VALEURS AUTORISÉES UNIQUEMENT : Si une information ne correspond à aucune valeur de la liste ci-dessous, tu DOIS mettre "null".
3. PRIORITÉ : Si plusieurs options valides apparaissent, prends la première.
4. FORMAT : Retourne un tableau d'objets [{}, {}]. Crée un objet par catégorie mentionnée.

### RÈGLE DE SORTIE FINALE (STRICTE) :
- Réponds EXCLUSIVEMENT avec le bloc JSON.
- INTERDICTION de saluer, d'expliquer ta démarche ou d'ajouter du texte avant ou après le JSON.
- Pas de balises Markdown de type ```json ... ```, renvoie uniquement le texte brut au format JSON.

### DICTIONNAIRE DE CORRESPONDANCE (Mapping) :

- nature_operation :
  * "Réhabilitation" (si : réhabilitation, rénovation, restructuration, réhabilités)
  * "Neuve" (si : neuf, construction, création)
  * "Extension" (si : agrandissement, extension)
  * "Rénovation thermique" (si : énergétique, thermique, CRE, MGP)

- type_infrastructure : 
  * "Scolaire" (si : collège, lycée, école, enseignement, restauration scolaire)
  * "Commerce" (si : restaurant, magasin, boutique)
  * "Sportif" (si : gymnase, stade, terrain)
  * "Logements" (si : appartement, habitat, immeuble)
  * "Tertiaire" (si : bureaux, administration, équipement public administratif)

- site_occupe : 
  * True (si : "site occupé", "en fonctionnement", "milieu habité")
  * False (si non mentionné ou explicitement vide)

- nombre_références : Extraire le chiffre associé au besoin de la catégorie (ex: "5 références par catégorie" -> 5).

### FORMAT DE SORTIE ATTENDU :
[
  {
    "catégorie": "Nom ou numéro de la catégorie",
    "nombre_références": number | null,
    "nature_operation": "Réhabilitation" | "Neuve" | "Extension" | "Rénovation thermique" | null,
    "site_occupe": boolean | null,
    "surface_SDP_minimum": number | null,
    "type_infrastructure": "Logements" | "Sportif" | "Résidence" | "Tertiaire" | "Scolaire" | "Commerce" | null,
    "anciennete_max_projet": number | null
  }
]

Ne repond rien d'autre que le format de sortie attendu
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

questions_rag = [
    {
        "llm": "Qu'est-ce qui est prévue pour ce projet? L'information est dans le header",
        "rerank": "Type de projet (école, gymnase, équipement culturel, bâtiment administratif)",
        "user": "Quel est le type d'infrastructure ?",
        "keyword": "Type"
    },
    {
        "llm": "Quelle est la nature de l’opération (construction neuve, extension, réhabilitation, rénovation, restructuration) ?",
        "rerank": "Nature du projet (neuf, extension, réhabilitation, rénovation, restructuration)",
        "user": "Quel est la nature de l'opération ?",
        "keyword" : "Nature"
    },
    {
        # "llm": "Donne moi le montant prévisionnel des travaux/projet indiqué dans le document ? Ou n'importe quel montant proposer par le document en echange de services. Explique a quoi sert le prix donner",
        "llm": "Analyse le document et indique le montant financier associé au projet (estimation, plafond, budget ou valeur du marché). Si plusieurs montants apparaissent, mentionne-les. Pour chaque montant, explique ce qu’il représente (limite maximale, coût prévu, montant contractuel, etc.) et à quoi il sert dans la consultation.",
        "rerank": "Montant/prix/cout prévisionnel du projet",
        "user": "Quel est le montant prévisionnel des travaux ?",
        "keyword" : "Travaux"
    },
    {
        "llm": "Dans quelle région administrative se situe le projet en te basant sur le texte fourni?",
        "rerank": "Région administrative du projet",
        "user": "Dans quelle région administratif se situe le projet ?",
        "keyword": "Region"
    },
    {
        "llm": "Extrait le(s) code(s) postal ou le(s) département(s) dans lequel se situe le projet",
        "rerank": "Dans quel code postal/département se trouve le projet",
        "user": "Dans quel département se situe le projet ?",
        "keyword": "Département"
    },
    {
        "llm": "Extrait uniquement le nom de la ville mentionnée dans le texte ci-dessous. Réponds uniquement par le nom de la ville, sans phrase, sans ponctuation, sans explication.S’il n’y a pas de ville clairement identifiable, réponds exactement par : AUCUNE.",
        "keyword": "Ville",
        "user": "Quelle est le nom de la ville ou se situe le projet?",
        "rerank": "Commune ou ville du projet"
    },
    {
        "llm": "Quelle est la succursale ou l’agence territoriale la plus proche mentionnée dans le document ?",
        "keyword": "Succursale",
        "user": "Quelle est la succursale ou l'agence territoriale la plus proche ?",
        "rerank": "Succursale ou agence territoriale la plus proche"
    },
    {
        "llm": "Qui est le maître d'ouvrage et quelles sont les informations que tu peux en extraire ? Si tu n'en as aucune répond juste avec le nom de maitre d'ouvrage",
        "keyword": "Ouvrage",
        "user": "Qui est le maitre d'ouvrages?",
        "rerank": "Maître d’ouvrage"
    },
    {
        "llm": "Extraits le numéro de telephone, l'adresse, l'adresse mail, le site web et le nom du mandataire dans ce format'Nom de la commune: Nom de la commune - Tél: numero de telephone OBLIGATOIREMENT a 10 chiffres - Représentant de l'acheteur: Nom du representant, site de l'acheteur: site - Adresse mail de l'acheteur: mail' et n'ajoute rien d'autres que ces infos, ne réponds pas si l'info n'est pas fournie. Il y aura surement les mots 'Affaire suivie par' a cote du nom",
        "keyword": "Mandataire",
        "user": "Qui est le mandataire du projet si il y en a un?",
        "rerank": "Mandataire du projet agissant pour le compte du maître d'ouvrage"
    },
    {
        "llm": "Quel est le type de sélection prévu (appel à candidatures ou appel d’offres) ?",
        "keyword": "Candidature",
        "user": "Quel est le type de sélection prévue?",
        "rerank": "Type de sélection (appel à candidatures / appel d’offres)"
    },
    {
        "llm": "Quel est le type de procédure de passation du marché (appel d’offres, concours, marché global de performance, procédure adaptée, etc.) ?",
        "keyword": "Procédure",
        "user": "Quel est le type de procédure de passation du marché ?",
        "rerank": "Type de procédure (AO, concours, MGP, etc.)"
    },
    {
        "llm": "Le document précise-t-il qu’un mandataire est requis ? Si oui, quel type de mandataire est demandé ?",
        "keyword": "Mandataire-requis",
        "user": "Qui est le mandataire requis et quel est son type si il y en a un",
        "rerank": "Mandataire requis et type"
    },
    {
        "llm": "Quelle est la date limite de remise des candidatures ou des offres (première échéance) ?",
        "keyword": "limite1", ##
        "user": "Quelle est la date limite de remise des candidatures ?",
        "rerank": "Quelle est la date limite de remise des candidatures"
    },
    {
        "llm": "Quelle est la date limite pour poser des questions ou demander des précisions auprès du maître d’ouvrage ?",
        "keyword": "Questions",
        "user": "Quelle est la date limite pour demander des renseignements supplémentaires?",
        "rerank": "Date limite pour questions"
    },
    {
        "llm": "Quelle est la date limite de remise des offres ou des candidatures (seconde échéance), si elle est mentionnée ?",
        "user": "Quelle est la data limite de remises des candidatures (seconde échéance)?",
        "keyword": "Seconde échéance",
        "rerank": "Seconde échéance date limite de remise des candidatures"
    },
    {
        "llm": "Une exclusivité est-elle imposée aux bureaux d’études ? Si oui, sur combien d’équipes cette exclusivité s’applique-t-elle ?",
        "rerank": "Exclusivité bureaux d’études (oui/non) et nombre d’équipes",
        "user" : "Y a t il une exclusivité sur les bureaux d'études et sur combien d'équipes ?",
        # "rerank": "Le document prévoit-il une exclusivité imposée pour les bureaux d’études ?",
        "keyword": "Exclusivité"
    },
    {
        # "llm": "Une visite du site est-elle prévue ? Si oui, à quelle date ?",
        # "rerank": "Y a t-il un rendez-vous sur site ?",
        # "keyword": "Visite"
        "llm": "Le document mentionne-t-il une visite, une réunion ou un déplacement sur site prévu pour les candidats ou les participants ? Si oui à quelle date ?",
        "rerank": "Présence sur site, réunion ou visite organisée dans le cadre du projet ou du concours ?",
        "user" : "Est-ce qu'une visite du site est obligatoire?",
        "keyword": "Présence sur site"
    },
    {
        "llm": "Quelles sont les compétences ou spécialités exigées pour la constitution de l’équipe candidate ?",
        "rerank": "Compétences ou spécialités requises pour l’équipe",
        "user": "Quelles sont les compétences exigées pour la constitution de l'équipe ?",
        "keyword": "Compétences"
    },
    {
        "llm": "Combien de références professionnelles au total sont demandées au groupement dans le cadre de la candidature ? Detail en disant combien de references pqr cqtegorie et quel categorie si cela est possible",
        "rerank": "Combien de références sont demandées à l’architecte?",
        "user": "Combien de références minimum sont demandées a l'architecte?",
        "keyword": "Références"
    },
    {
        "llm": "Quelles sont les missions confiées au titulaire du marché (par exemple : mission complète, DIAG, FAISA, REL, EXE, etc.) ?",
        "rerank": "Missions demandées (mission complète, DIAG, FAISA, REL, EXE, etc.)",
        "user": "Quelles sont les missions demandées au titulaire du marché",
        "keyword": "Missions"
    },
    {
        "llm": "Le marché est-il découpé en tranches ? Si oui, combien de tranches sont prévues et quelles sont leurs natures (tranche ferme, tranche optionnelle) ?",
        "rerank": "Le marché est-il découpé en tranches (nombre et type : ferme / optionnelle)",
        "user": "Le marché est-il découpé en tranches? Si oui, lesquelles?",
        "keyword": "Tranches"
    },
    {
        "llm": "Quelles sont les phases de la mission, combien sont-elles et quelle est leur temporalité prévisionnelle ?",
        "rerank": "Phases de la mission (nombre et temporalité)",
        "user": "Quelles sont les phases de la mission?",
        "keyword": "Phases"
    },
    {
        # "llm": "Le projet prévoit-il l’intervention d’une AMO ou d’un MOD ? Si oui, lequel et par qui est-il assuré ?",
        # "rerank": "AMO ou MOD et entité concernée"
        "llm": "Le projet prévoit-il l’intervention d’une assistance à maîtrise d’ouvrage ou d’un maître d’ouvrage délégué ? Si oui, lequel et quelle entité en est responsable ?",
        "rerank": "Assistance à maîtrise d’ouvrage ou maîtrise d’ouvrage déléguée et entité responsable",
        "user": "Le projet prévoit il l'intervention d'une assistance a maitrise d'ouvrages?",
        "keyword": "Assistances"
    },
    {
        "llm": "Une prime de concours est-elle prévue ? Si oui, quel est le montant de cette prime ?",
        # "rerank": "Prime de concours (oui/non) et montant",
        "rerank": "Remise ou versement de prime avec montant",
        "user": "Une prime de concours est-elle prévue? Si oui, quel est son montant?",
        "keyword": "Prime"
    },
    {
        "llm": "Le document impose-t-il la réalisation d’une maquette (numérique ou physique) dans le cadre de la candidature ou de l’offre ?Si aucune information n'est fourni à ce sujet réponds seulement'Non précisé'",
        "rerank": "Maquette requise (oui/non)",
        "user": "La réalisation d'une maquette est elle imposé?",
        "keyword": "Maquette"
    },
    {
        "llm": "La réalisation d’un film de présentation est-elle exigée dans le cadre de la procédure ? Si aucune information n'est fourni à ce sujet réponds seulement'Non précisé'",
        "rerank": "Film requis (oui/non)",
        "user": "La réalisation d'un film est-elle imposée?",
        "keyword": "Film"
    },
    {
        "llm": "Un numéro de consultation se trouve probablment dans les extraits fournis. Extrais ce qui te semble être le numéro de consultation si rien n'y correspond répond 'Information non précisé'",
        "rerank": "Numéro de consultation ou d'appel d'offres",
        "user": "Quel est le numéro de consultation ou d'appel d'offres?",
        "keyword": "Numéro"
    },
    {
        "llm": "Quel est le type d'opération, sur quelle infrastructure et ou se situe l'infrastruscture en question ? Si tu ne trouves pas la réponses dans les extraits fournis répond 'Non précisé'",
        "rerank": "Type d'opération et infrastructure",
        "user": "Quel est le type d'opération et sur quelle infrastructure ?",
        "keyword": "Type d'opération"
    },
    {
        "llm": "Extraits toutes les informations concernant les références demandés",
        "rerank": "Nombres et types de références demandés",
        "user": "ref",
        "keyword": "Références"
    },
    {
        "llm": "Quels sont les critères d’appréciation ou d’évaluation mentionnés dans le texte et quels sont leurs pourcentages respectifs ?",
        "rerank": "Critères d’appréciation ou d’évaluation d’une offre avec pondération ou pourcentage (prix, valeur technique, délais).",
        "user": "Pourcentages",
        "keyword": "pourcentages"
    }
]