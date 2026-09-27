import sqlite3


DATABASE_PATH = "aura.db"


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
        if not column_exists(
            conn,
            "tasks",
            "user_id",
        ):
            conn.execute(
                """
                ALTER TABLE tasks
                ADD COLUMN user_id INTEGER
                REFERENCES users(id)
                """
            )

        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS
            ix_tasks_user_id
            ON tasks(user_id)
            """
        )

        conn.commit()

    finally:
        conn.close()


if __name__ == "__main__":
    run_migration()