"""
Base SQLite pour stocker les questions RAG.
L'utilisateur peut ajouter, modifier, supprimer des questions.
"""
import sqlite3
import os
from typing import Any

# Fichier DB à la racine du projet
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "questions.db")


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Crée la table si elle n'existe pas et la remplit avec les questions par défaut si vide."""
    conn = _get_conn()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                llm TEXT NOT NULL,
                rerank TEXT NOT NULL,
                user TEXT NOT NULL,
                keyword TEXT NOT NULL,
                order_index INTEGER NOT NULL DEFAULT 0
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lot_numero TEXT,
                identification TEXT,
                prestations TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS mandataires (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom_commercial_denomination TEXT,
                adresses_postale_siege TEXT,
                adresse_electronique TEXT,
                telephone_telecopie TEXT,
                siret_ou_identification TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS dc2_operateurs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lot_numero TEXT,
                nom_membre_groupement TEXT,
                identification TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memo_administrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT DEFAULT '',
                role_phase_etudes TEXT DEFAULT '',
                role_phase_chantier TEXT DEFAULT '',
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memo_moyens_humains (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                administration_id INTEGER NOT NULL,
                nom TEXT,
                description TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY(administration_id) REFERENCES memo_administrations(id) ON DELETE CASCADE
            )
        """)
        # Migration légère: ajoute les colonnes manquantes si la table existe déjà.
        _ensure_column(conn, "memo_administrations", "description", "TEXT DEFAULT ''")
        _ensure_column(conn, "memo_administrations", "role_phase_etudes", "TEXT DEFAULT ''")
        _ensure_column(conn, "memo_administrations", "role_phase_chantier", "TEXT DEFAULT ''")
        conn.commit()
        cur = conn.execute("SELECT COUNT(*) FROM questions")
        if cur.fetchone()[0] == 0:
            _seed_default_questions(conn)
    finally:
        conn.close()


def _ensure_column(conn: sqlite3.Connection, table_name: str, column_name: str, sql_type: str) -> None:
    cols = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    names = {c["name"] if isinstance(c, sqlite3.Row) else c[1] for c in cols}
    if column_name not in names:
        conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {sql_type}")


def _seed_default_questions(conn: sqlite3.Connection) -> None:
    """Insère les questions par défaut (celles de chunk.questions_rag)."""
    import backend.prompt_list as prompt
    for i, q in enumerate(prompt.questions_rag):
        conn.execute(
            "INSERT INTO questions (llm, rerank, user, keyword, order_index) VALUES (?, ?, ?, ?, ?)",
            (
                q.get("llm", ""),
                q.get("rerank", ""),
                q.get("user", ""),
                q.get("keyword", ""),
                i,
            ),
        )
    conn.commit()


def sync_from_default_questions() -> list[dict[str, Any]]:
    """
    Remplace tout le contenu de la table par la liste questions_rag de chunk.py.
    À appeler quand tu veux « remettre la base à jour » avec le code.
    """
    init_db()
    conn = _get_conn()
    try:
        conn.execute("DELETE FROM questions")
        conn.commit()
        _seed_default_questions(conn)
    finally:
        conn.close()
    return get_all_questions()


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return dict(zip(row.keys(), row)) if row else {}


def get_all_questions() -> list[dict[str, Any]]:
    """Retourne toutes les questions triées par order_index."""
    init_db()
    conn = _get_conn()
    try:
        cur = conn.execute(
            "SELECT id, llm, rerank, user, keyword, order_index FROM questions ORDER BY order_index ASC, id ASC"
        )
        return [_row_to_dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def add_question(llm: str, rerank: str, user: str, keyword: str) -> dict[str, Any]:
    """Ajoute une question et retourne la question créée avec son id."""
    init_db()
    conn = _get_conn()
    try:
        cur = conn.execute(
            "SELECT COALESCE(MAX(order_index), -1) + 1 FROM questions"
        )
        order_index = cur.fetchone()[0]
        cur = conn.execute(
            "INSERT INTO questions (llm, rerank, user, keyword, order_index) VALUES (?, ?, ?, ?, ?)",
            (llm, rerank, user, keyword, order_index),
        )
        conn.commit()
        row = conn.execute("SELECT id, llm, rerank, user, keyword, order_index FROM questions WHERE id = ?", (cur.lastrowid,)).fetchone()
        return _row_to_dict(row)
    finally:
        conn.close()


def delete_question(question_id: int) -> bool:
    """Supprime une question. Retourne True si une ligne a été supprimée."""
    init_db()
    conn = _get_conn()
    try:
        cur = conn.execute("DELETE FROM questions WHERE id = ?", (question_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def get_all_members() -> list[dict[str, Any]]:
    """Retourne tous les membres enregistrés individuellement."""
    init_db()
    conn = _get_conn()
    try:
        cur = conn.execute(
            "SELECT id, lot_numero, identification, prestations, created_at FROM members ORDER BY created_at ASC"
        )
        return [
            {
                "id": r["id"],
                "lotNumero": r["lot_numero"] or "",
                "identification": r["identification"] or "",
                "prestations": r["prestations"] or "",
                "created_at": r["created_at"],
            }
            for r in cur.fetchall()
        ]
    finally:
        conn.close()


def add_member(lot_numero: str, identification: str, prestations: str) -> dict[str, Any]:
    """Enregistre un membre individuellement."""
    init_db()
    conn = _get_conn()
    try:
        cur = conn.execute(
            "INSERT INTO members (lot_numero, identification, prestations) VALUES (?, ?, ?)",
            (lot_numero or "", identification or "", prestations or ""),
        )
        conn.commit()
        row = conn.execute(
            "SELECT id, lot_numero, identification, prestations, created_at FROM members WHERE id = ?",
            (cur.lastrowid,),
        ).fetchone()
        return {
            "id": row["id"],
            "lotNumero": row["lot_numero"] or "",
            "identification": row["identification"] or "",
            "prestations": row["prestations"] or "",
            "created_at": row["created_at"],
        }
    finally:
        conn.close()


def delete_member(member_id: int) -> bool:
    """Supprime un membre."""
    init_db()
    conn = _get_conn()
    try:
        cur = conn.execute("DELETE FROM members WHERE id = ?", (member_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def get_all_mandataires() -> list[dict[str, Any]]:
    """Retourne tous les mandataires enregistrés."""
    init_db()
    conn = _get_conn()
    try:
        cur = conn.execute(
            """SELECT id, nom_commercial_denomination, adresses_postale_siege,
               adresse_electronique, telephone_telecopie, siret_ou_identification, created_at
               FROM mandataires ORDER BY created_at ASC"""
        )
        return [
            {
                "id": r["id"],
                "nomCommercialDenomination": r["nom_commercial_denomination"] or "",
                "adressesPostaleSiege": r["adresses_postale_siege"] or "",
                "adresseElectronique": r["adresse_electronique"] or "",
                "telephoneTelecopie": r["telephone_telecopie"] or "",
                "siretOuIdentification": r["siret_ou_identification"] or "",
                "created_at": r["created_at"],
            }
            for r in cur.fetchall()
        ]
    finally:
        conn.close()


def add_mandataire(
    nom_commercial_denomination: str,
    adresses_postale_siege: str,
    adresse_electronique: str,
    telephone_telecopie: str,
    siret_ou_identification: str,
) -> dict[str, Any]:
    """Enregistre un mandataire."""
    init_db()
    conn = _get_conn()
    try:
        cur = conn.execute(
            """INSERT INTO mandataires
               (nom_commercial_denomination, adresses_postale_siege, adresse_electronique,
                telephone_telecopie, siret_ou_identification)
               VALUES (?, ?, ?, ?, ?)""",
            (
                nom_commercial_denomination or "",
                adresses_postale_siege or "",
                adresse_electronique or "",
                telephone_telecopie or "",
                siret_ou_identification or "",
            ),
        )
        conn.commit()
        row = conn.execute(
            """SELECT id, nom_commercial_denomination, adresses_postale_siege,
               adresse_electronique, telephone_telecopie, siret_ou_identification, created_at
               FROM mandataires WHERE id = ?""",
            (cur.lastrowid,),
        ).fetchone()
        return {
            "id": row["id"],
            "nomCommercialDenomination": row["nom_commercial_denomination"] or "",
            "adressesPostaleSiege": row["adresses_postale_siege"] or "",
            "adresseElectronique": row["adresse_electronique"] or "",
            "telephoneTelecopie": row["telephone_telecopie"] or "",
            "siretOuIdentification": row["siret_ou_identification"] or "",
            "created_at": row["created_at"],
        }
    finally:
        conn.close()


def delete_mandataire(mandataire_id: int) -> bool:
    """Supprime un mandataire."""
    init_db()
    conn = _get_conn()
    try:
        cur = conn.execute("DELETE FROM mandataires WHERE id = ?", (mandataire_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def get_all_dc2_operateurs() -> list[dict[str, Any]]:
    """Retourne tous les opérateurs DC2 (Module H) enregistrés."""
    init_db()
    conn = _get_conn()
    try:
        cur = conn.execute(
            "SELECT id, lot_numero, nom_membre_groupement, identification, created_at FROM dc2_operateurs ORDER BY created_at ASC"
        )
        return [
            {
                "id": r["id"],
                "lotNumero": r["lot_numero"] or "",
                "nomMembreGroupement": r["nom_membre_groupement"] or "",
                "identification": r["identification"] or "",
                "created_at": r["created_at"],
            }
            for r in cur.fetchall()
        ]
    finally:
        conn.close()


def add_dc2_operateur(lot_numero: str, nom_membre_groupement: str, identification: str) -> dict[str, Any]:
    """Enregistre un opérateur DC2 (Module H)."""
    init_db()
    conn = _get_conn()
    try:
        cur = conn.execute(
            "INSERT INTO dc2_operateurs (lot_numero, nom_membre_groupement, identification) VALUES (?, ?, ?)",
            (lot_numero or "", nom_membre_groupement or "", identification or ""),
        )
        conn.commit()
        row = conn.execute(
            "SELECT id, lot_numero, nom_membre_groupement, identification, created_at FROM dc2_operateurs WHERE id = ?",
            (cur.lastrowid,),
        ).fetchone()
        return {
            "id": row["id"],
            "lotNumero": row["lot_numero"] or "",
            "nomMembreGroupement": row["nom_membre_groupement"] or "",
            "identification": row["identification"] or "",
            "created_at": row["created_at"],
        }
    finally:
        conn.close()


def delete_dc2_operateur(operateur_id: int) -> bool:
    """Supprime un opérateur DC2."""
    init_db()
    conn = _get_conn()
    try:
        cur = conn.execute("DELETE FROM dc2_operateurs WHERE id = ?", (operateur_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def get_all_memo_administrations() -> list[dict[str, Any]]:
    """Retourne les administrations de la note méthodologique."""
    init_db()
    conn = _get_conn()
    try:
        cur = conn.execute(
            "SELECT id, name, created_at FROM memo_administrations ORDER BY name COLLATE NOCASE ASC"
        )
        return [
            {
                "id": r["id"],
                "name": r["name"] or "",
                "created_at": r["created_at"],
            }
            for r in cur.fetchall()
        ]
    finally:
        conn.close()


def add_memo_administration(name: str) -> dict[str, Any]:
    """Crée une administration (ou retourne l'existante si même nom)."""
    init_db()
    clean = (name or "").strip()
    if not clean:
        raise ValueError("Le nom d'administration est requis.")
    conn = _get_conn()
    try:
        existing = conn.execute(
            "SELECT id, name, description, role_phase_etudes, role_phase_chantier, created_at FROM memo_administrations WHERE lower(name) = lower(?)",
            (clean,),
        ).fetchone()
        if existing:
            return {
                "id": existing["id"],
                "name": existing["name"] or "",
                "description": existing["description"] or "",
                "rolePhaseEtudes": existing["role_phase_etudes"] or "",
                "rolePhaseChantier": existing["role_phase_chantier"] or "",
                "created_at": existing["created_at"],
            }
        cur = conn.execute(
            "INSERT INTO memo_administrations (name) VALUES (?)",
            (clean,),
        )
        conn.commit()
        row = conn.execute(
            "SELECT id, name, description, role_phase_etudes, role_phase_chantier, created_at FROM memo_administrations WHERE id = ?",
            (cur.lastrowid,),
        ).fetchone()
        return {
            "id": row["id"],
            "name": row["name"] or "",
            "description": row["description"] or "",
            "rolePhaseEtudes": row["role_phase_etudes"] or "",
            "rolePhaseChantier": row["role_phase_chantier"] or "",
            "created_at": row["created_at"],
        }
    finally:
        conn.close()


def delete_memo_administration(administration_id: int) -> bool:
    """Supprime une administration et ses moyens humains associés."""
    init_db()
    conn = _get_conn()
    try:
        conn.execute(
            "DELETE FROM memo_moyens_humains WHERE administration_id = ?",
            (administration_id,),
        )
        cur = conn.execute(
            "DELETE FROM memo_administrations WHERE id = ?",
            (administration_id,),
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def get_memo_administration_profile(administration_id: int) -> dict[str, Any] | None:
    """Retourne le profil complet d'une administration (roles + moyens humains)."""
    init_db()
    conn = _get_conn()
    try:
        admin = conn.execute(
            """SELECT id, name, description, role_phase_etudes, role_phase_chantier, created_at
               FROM memo_administrations WHERE id = ?""",
            (administration_id,),
        ).fetchone()
        if not admin:
            return None
        cur = conn.execute(
            """SELECT id, nom, description, created_at
               FROM memo_moyens_humains
               WHERE administration_id = ?
               ORDER BY id ASC""",
            (administration_id,),
        )
        moyens = [
            {
                "id": r["id"],
                "nom": r["nom"] or "",
                "description": r["description"] or "",
                "created_at": r["created_at"],
            }
            for r in cur.fetchall()
        ]
        return {
            "id": admin["id"],
            "name": admin["name"] or "",
            "description": admin["description"] or "",
            "rolePhaseEtudes": admin["role_phase_etudes"] or "",
            "rolePhaseChantier": admin["role_phase_chantier"] or "",
            "moyensHumains": moyens,
            "created_at": admin["created_at"],
        }
    finally:
        conn.close()


def save_memo_administration_profile(
    administration_id: int,
    description: str,
    role_phase_etudes: str,
    role_phase_chantier: str,
    moyens_humains: list[dict[str, Any]] | None,
) -> dict[str, Any] | None:
    """Enregistre le profil d'une administration et remplace sa liste de moyens humains."""
    init_db()
    conn = _get_conn()
    try:
        exists = conn.execute(
            "SELECT id FROM memo_administrations WHERE id = ?",
            (administration_id,),
        ).fetchone()
        if not exists:
            return None
        conn.execute(
            """UPDATE memo_administrations
               SET description = ?, role_phase_etudes = ?, role_phase_chantier = ?
               WHERE id = ?""",
            (description or "", role_phase_etudes or "", role_phase_chantier or "", administration_id),
        )
        conn.execute(
            "DELETE FROM memo_moyens_humains WHERE administration_id = ?",
            (administration_id,),
        )
        for mh in moyens_humains or []:
            nom = str(mh.get("nom", "") if isinstance(mh, dict) else "").strip()
            desc = str(mh.get("description", "") if isinstance(mh, dict) else "").strip()
            if not nom and not desc:
                continue
            conn.execute(
                "INSERT INTO memo_moyens_humains (administration_id, nom, description) VALUES (?, ?, ?)",
                (administration_id, nom, desc),
            )
        conn.commit()
    finally:
        conn.close()
    return get_memo_administration_profile(administration_id)


def update_question(question_id: int, llm: str | None = None, rerank: str | None = None, user: str | None = None, keyword: str | None = None) -> dict[str, Any] | None:
    """Met à jour une question. Retourne la question mise à jour ou None si id inconnu."""
    init_db()
    conn = _get_conn()
    try:
        updates = []
        args = []
        if llm is not None:
            updates.append("llm = ?")
            args.append(llm)
        if rerank is not None:
            updates.append("rerank = ?")
            args.append(rerank)
        if user is not None:
            updates.append("user = ?")
            args.append(user)
        if keyword is not None:
            updates.append("keyword = ?")
            args.append(keyword)
        if not updates:
            row = conn.execute("SELECT id, llm, rerank, user, keyword, order_index FROM questions WHERE id = ?", (question_id,)).fetchone()
            return _row_to_dict(row) if row else None
        args.append(question_id)
        conn.execute(f"UPDATE questions SET {', '.join(updates)} WHERE id = ?", args)
        conn.commit()
        row = conn.execute("SELECT id, llm, rerank, user, keyword, order_index FROM questions WHERE id = ?", (question_id,)).fetchone()
        return _row_to_dict(row) if row else None
    finally:
        conn.close()
