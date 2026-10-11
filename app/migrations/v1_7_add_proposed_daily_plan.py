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
            "daily_plans",
            "proposed_plan_data",
        ):
            conn.execute(
                """
                ALTER TABLE daily_plans
                ADD COLUMN proposed_plan_data JSON
                """
            )

        conn.commit()

    finally:
        conn.close()


if __name__ == "__main__":
    run_migration()