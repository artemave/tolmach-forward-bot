"""SQLite persistence: per-user language, level, and last translated post.

A single ``users`` table keyed by Telegram user ID holds everything.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Self

import aiosqlite

_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id          INTEGER PRIMARY KEY,
    target_language  TEXT,
    level            TEXT,
    last_original    TEXT,
    last_translation TEXT,
    created_at       TEXT NOT NULL,
    updated_at       TEXT NOT NULL
)
"""

_SELECT_USER = """
SELECT user_id, target_language, level, last_original, last_translation, created_at, updated_at
FROM users
WHERE user_id = ?
"""

_SET_LANGUAGE = """
INSERT INTO users (user_id, target_language, created_at, updated_at)
VALUES (?, ?, ?, ?)
ON CONFLICT(user_id) DO UPDATE SET
    target_language = excluded.target_language,
    updated_at = excluded.updated_at
"""

_SET_LEVEL = """
INSERT INTO users (user_id, level, created_at, updated_at)
VALUES (?, ?, ?, ?)
ON CONFLICT(user_id) DO UPDATE SET
    level = excluded.level,
    updated_at = excluded.updated_at
"""

_SAVE_LAST_POST = """
INSERT INTO users (user_id, last_original, last_translation, created_at, updated_at)
VALUES (?, ?, ?, ?, ?)
ON CONFLICT(user_id) DO UPDATE SET
    last_original = excluded.last_original,
    last_translation = excluded.last_translation,
    updated_at = excluded.updated_at
"""


@dataclass(frozen=True, slots=True)
class User:
    """A persisted user and their current configuration."""

    user_id: int
    target_language: str | None
    level: str | None
    last_original: str | None
    last_translation: str | None
    created_at: str
    updated_at: str

    @property
    def is_configured(self) -> bool:
        """Whether both a target language and a CEFR level have been set."""
        return self.target_language is not None and self.level is not None


def _now() -> str:
    return datetime.now(UTC).isoformat()


class Database:
    """Async wrapper around the single-table SQLite store."""

    def __init__(self, connection: aiosqlite.Connection) -> None:
        """Wrap an already-open aiosqlite connection."""
        self._connection = connection

    @classmethod
    async def connect(cls, path: str) -> Self:
        """Open ``path``, create the schema if needed, and return a ready database."""
        connection = await aiosqlite.connect(path)
        connection.row_factory = aiosqlite.Row
        database = cls(connection)
        await database._init_schema()
        return database

    async def _init_schema(self) -> None:
        await self._connection.execute(_SCHEMA)
        await self._connection.commit()

    async def close(self) -> None:
        """Close the underlying connection."""
        await self._connection.close()

    async def get_user(self, user_id: int) -> User | None:
        """Return the stored user, or ``None`` if they have no row yet."""
        async with self._connection.execute(_SELECT_USER, (user_id,)) as cursor:
            row = await cursor.fetchone()
        if row is None:
            return None
        return User(
            user_id=row["user_id"],
            target_language=row["target_language"],
            level=row["level"],
            last_original=row["last_original"],
            last_translation=row["last_translation"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    async def set_language(self, user_id: int, language: str) -> None:
        """Set the user's target language, creating their row if needed."""
        now = _now()
        await self._connection.execute(_SET_LANGUAGE, (user_id, language, now, now))
        await self._connection.commit()

    async def set_level(self, user_id: int, level: str) -> None:
        """Set the user's CEFR level, creating their row if needed."""
        now = _now()
        await self._connection.execute(_SET_LEVEL, (user_id, level, now, now))
        await self._connection.commit()

    async def save_last_post(self, user_id: int, original: str, translation: str) -> None:
        """Store the most recent original text and its translation for ``user_id``."""
        now = _now()
        await self._connection.execute(
            _SAVE_LAST_POST,
            (user_id, original, translation, now, now),
        )
        await self._connection.commit()
