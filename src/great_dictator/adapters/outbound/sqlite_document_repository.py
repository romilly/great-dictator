from __future__ import annotations

import sqlite3
from dataclasses import replace
from datetime import datetime

from great_dictator.domain.document import (
    Document,
    DocumentRepositoryPort,
    DocumentSummary,
)


class SqliteDocumentRepository(DocumentRepositoryPort):
    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user TEXT NOT NULL DEFAULT 'romilly',
                    name TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created TEXT NOT NULL,
                    UNIQUE(user, name)
                )
            """)
            conn.commit()

    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self._db_path)

    def save(self, document: Document) -> Document:
        with self._get_connection() as conn:
            if document.id is not None:
                # Update existing
                conn.execute(
                    """
                    UPDATE documents SET user=?, name=?, content=?, created=?
                    WHERE id=?
                    """,
                    (
                        document.user,
                        document.name,
                        document.content,
                        document.created.isoformat(),
                        document.id,
                    ),
                )
                conn.commit()
                return document
            else:
                # Insert new
                cursor = conn.execute(
                    """
                    INSERT INTO documents (user, name, content, created)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        document.user,
                        document.name,
                        document.content,
                        document.created.isoformat(),
                    ),
                )
                conn.commit()
                return replace(document, id=cursor.lastrowid)

    def load(self, document_id: int) -> Document | None:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT id, user, name, content, created FROM documents WHERE id=?",
                (document_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return Document(
                id=row[0],
                user=row[1],
                name=row[2],
                content=row[3],
                created=datetime.fromisoformat(row[4]),
            )

    def list_for_user(self, user: str) -> list[DocumentSummary]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT id, name, created FROM documents WHERE user=?",
                (user,),
            )
            return [
                DocumentSummary(
                    id=row[0],
                    name=row[1],
                    created=datetime.fromisoformat(row[2]),
                )
                for row in cursor.fetchall()
            ]

    def delete(self, document_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM documents WHERE id=?",
                (document_id,),
            )
            conn.commit()
            return cursor.rowcount > 0
