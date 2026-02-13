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
        conn.commit()
        cur = conn.execute("SELECT COUNT(*) FROM questions")
        if cur.fetchone()[0] == 0:
            _seed_default_questions(conn)
    finally:
        conn.close()


def _seed_default_questions(conn: sqlite3.Connection) -> None:
    """Insère les questions par défaut (celles de chunk.questions_rag)."""
    import backend.chunk as chunk
    for i, q in enumerate(chunk.questions_rag):
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
