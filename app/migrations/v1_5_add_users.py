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
            "users",
        ):
            conn.execute(
                """
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100),
                    created_at DATETIME NOT NULL
                        DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME NOT NULL
                        DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

        if (
            table_exists(
                conn,
                "conversation_context",
            )
            and not column_exists(
                conn,
                "conversation_context",
                "user_id",
            )
        ):
            conn.execute(
                """
                ALTER TABLE conversation_context
                ADD COLUMN user_id INTEGER
                REFERENCES users(id)
                """
            )

        conn.commit()

    finally:
        conn.close()


if __name__ == "__main__":
    run_migration()