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
                    id INTEGER PRIMARY KEY,
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

        conn.commit()

    finally:
        conn.close()


if __name__ == "__main__":
    run_migration()