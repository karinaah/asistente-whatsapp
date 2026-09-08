import sqlite3


DATABASE_PATH = "aura.db"


def table_exists(
    conn: sqlite3.Connection,
    table_name: str,
) -> bool:
    result = conn.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        AND name = ?
        """,
        (table_name,),
    ).fetchone()

    return result is not None


def column_exists(
    conn: sqlite3.Connection,
    table_name: str,
    column_name: str,
) -> bool:
    columns = conn.execute(
        f"PRAGMA table_info({table_name})"
    ).fetchall()

    return any(
        column[1] == column_name
        for column in columns
    )


def run_migration() -> None:
    conn = sqlite3.connect(DATABASE_PATH)

    try:
        if not table_exists(
            conn,
            "conversation_context",
        ):
            conn.execute(
                """
                CREATE TABLE conversation_context (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id VARCHAR(100)
                        NOT NULL UNIQUE,
                    last_intent VARCHAR(50),
                    last_recommendation JSON,
                    last_plan JSON,
                    awaiting_remaining_minutes BOOLEAN
                        NOT NULL DEFAULT 0,
                    pending_active_task_id INTEGER,
                    updated_at DATETIME NOT NULL
                        DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

        elif not column_exists(
            conn,
            "conversation_context",
            "session_id",
        ):
            conn.execute(
                """
                ALTER TABLE conversation_context
                ADD COLUMN session_id VARCHAR(100)
                """
            )

            conn.execute(
                """
                UPDATE conversation_context
                SET session_id = 'default'
                WHERE session_id IS NULL
                """
            )

            conn.execute(
                """
                CREATE UNIQUE INDEX
                IF NOT EXISTS
                ix_conversation_context_session_id
                ON conversation_context(session_id)
                """
            )

        conn.commit()

    finally:
        conn.close()


if __name__ == "__main__":
    run_migration()