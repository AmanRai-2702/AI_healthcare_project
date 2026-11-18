
import sqlite3
import uuid

from datetime import datetime, timezone
from pathlib import Path
from contextlib import contextmanager

# Resolve the project root independently of the working directory.
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DB_PATH = PROJECT_ROOT / "data" / "conversations.db"



@contextmanager
def get_connection():
    """Create, manage, and safely close a SQLite connection."""

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def current_timestamp():
    """Return the current UTC timestamp."""

    return datetime.now(timezone.utc).isoformat()


def init_db():
    """Initialize conversation and message tables."""

    with get_connection() as connection:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                conversation_id TEXT PRIMARY KEY,
                patient_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,

                FOREIGN KEY (conversation_id)
                REFERENCES conversations(conversation_id)
                ON DELETE CASCADE
            )
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_conversations_patient
            ON conversations(patient_id)
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_conversation
            ON messages(conversation_id, id)
        """)


def create_conversation(patient_id: str) -> str:
    """Create a new conversation for a patient."""

    if not isinstance(patient_id, str) or not patient_id.strip():
        raise ValueError("Patient ID cannot be empty.")

    init_db()

    conversation_id = str(uuid.uuid4())
    timestamp = current_timestamp()

    with get_connection() as connection:

        connection.execute(
            """
            INSERT INTO conversations (
                conversation_id,
                patient_id,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                conversation_id,
                patient_id.strip(),
                timestamp,
                timestamp,
            ),
        )

    return conversation_id


def validate_conversation(
    conversation_id: str,
    patient_id: str,
) -> bool:
    """Check whether a conversation belongs to the given patient."""

    if not conversation_id or not patient_id:
        return False

    init_db()

    with get_connection() as connection:

        result = connection.execute(
            """
            SELECT 1
            FROM conversations
            WHERE conversation_id = ?
              AND patient_id = ?
            """,
            (conversation_id, patient_id),
        ).fetchone()

    return result is not None


def save_message(
    conversation_id: str,
    patient_id: str,
    role: str,
    content: str,
):
    """Save a message after verifying conversation ownership."""

    if role not in ("user", "assistant"):
        raise ValueError("Role must be user or assistant.")

    if not isinstance(content, str) or not content.strip():
        raise ValueError("Message content cannot be empty.")

    init_db()

    timestamp = current_timestamp()

    with get_connection() as connection:

        result = connection.execute(
            """
            SELECT 1
            FROM conversations
            WHERE conversation_id = ?
              AND patient_id = ?
            """,
            (conversation_id, patient_id),
        ).fetchone()

        if result is None:
            raise ValueError("Conversation not found for this patient.")

        connection.execute(
            """
            INSERT INTO messages (
                conversation_id,
                role,
                content,
                created_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                conversation_id,
                role,
                content.strip(),
                timestamp,
            ),
        )

        connection.execute(
            """
            UPDATE conversations
            SET updated_at = ?
            WHERE conversation_id = ?
            """,
            (timestamp, conversation_id),
        )


def get_conversation_history(
    conversation_id: str,
    patient_id: str,
    limit: int = 20,
) -> list[dict]:
    """Retrieve recent messages belonging to a patient's conversation."""

    if limit < 1:
        raise ValueError("Limit must be at least 1.")

    init_db()

    with get_connection() as connection:

        result = connection.execute(
            """
            SELECT 1
            FROM conversations
            WHERE conversation_id = ?
              AND patient_id = ?
            """,
            (conversation_id, patient_id),
        ).fetchone()

        if result is None:
            raise ValueError("Conversation not found for this patient.")

        rows = connection.execute(
            """
            SELECT role, content, created_at
            FROM messages
            WHERE conversation_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (conversation_id, limit),
        ).fetchall()

    # Reverse the descending results into chronological order.
    return [
        {
            "role": row["role"],
            "content": row["content"],
            "created_at": row["created_at"],
        }
        for row in reversed(rows)
    ]


def list_conversations(
    patient_id: str,
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    """List a patient's conversations, newest activity first."""

    if not isinstance(patient_id, str) or not patient_id.strip():
        raise ValueError("Patient ID cannot be empty.")

    if limit < 1:
        raise ValueError("Limit must be at least 1.")

    if offset < 0:
        raise ValueError("Offset cannot be negative.")

    init_db()

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                c.conversation_id,
                c.created_at,
                c.updated_at,
                COUNT(m.id) AS message_count,
                (
                    SELECT content
                    FROM messages
                    WHERE conversation_id = c.conversation_id
                    ORDER BY id DESC
                    LIMIT 1
                ) AS last_message
            FROM conversations c
            LEFT JOIN messages m
                ON c.conversation_id = m.conversation_id
            WHERE c.patient_id = ?
            GROUP BY c.conversation_id
            ORDER BY c.updated_at DESC
            LIMIT ? OFFSET ?
            """,
            (patient_id.strip(), limit, offset),
        ).fetchall()

    return [
        {
            "conversation_id": row["conversation_id"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "message_count": row["message_count"],
            "last_message": row["last_message"],
        }
        for row in rows
    ]

def delete_conversation(
    conversation_id: str,
    patient_id: str,
) -> bool:
    """Delete a conversation belonging to the specified patient."""

    if not conversation_id or not patient_id:
        raise ValueError("Conversation ID and patient ID are required.")

    init_db()

    with get_connection() as connection:
        result = connection.execute(
            """
            DELETE FROM conversations
            WHERE conversation_id = ?
              AND patient_id = ?
            """,
            (conversation_id, patient_id),
        )

        return result.rowcount > 0
