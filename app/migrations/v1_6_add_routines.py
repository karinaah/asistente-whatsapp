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
            "routines",
        ):
            conn.execute(
                """
                CREATE TABLE routines (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    title VARCHAR(200) NOT NULL,
                    description VARCHAR(1000),
                    weekdays JSON NOT NULL,
                    preferred_start_time TIME,
                    estimated_minutes INTEGER NOT NULL,
                    category VARCHAR(30) NOT NULL,
                    context VARCHAR(20) NOT NULL,
                    workspace VARCHAR(20) NOT NULL,
                    activity_type VARCHAR(30)
                        NOT NULL DEFAULT 'routine',
                    active BOOLEAN
                        NOT NULL DEFAULT 1,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL,
                    FOREIGN KEY(user_id)
                        REFERENCES users(id)
                )
                """
            )

            conn.execute(
                """
                CREATE INDEX ix_routines_user_id
                ON routines(user_id)
                """
            )

        conn.commit()

    finally:
        conn.close()


if __name__ == "__main__":
    run_migration()