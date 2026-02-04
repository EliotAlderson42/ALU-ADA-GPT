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
