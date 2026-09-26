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
            "user_profiles",
        ):
            conn.execute(
                """
                CREATE TABLE user_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL UNIQUE,
                    created_at DATETIME NOT NULL
                        DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME NOT NULL
                        DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id)
                        REFERENCES users(id)
                )
                """
            )

        conn.commit()

    finally:
        conn.close()


if __name__ == "__main__":
    run_migration()