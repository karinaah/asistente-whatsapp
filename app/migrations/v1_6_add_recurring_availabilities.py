from sqlalchemy import inspect, text

from app.config.database import engine


TABLE_NAME = "recurring_availabilities"


def table_exists() -> bool:
    inspector = inspect(engine)
    return TABLE_NAME in inspector.get_table_names()


def migrate():
    if table_exists():
        print(
            "Table recurring_availabilities "
            "already exists."
        )
        return

    with engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE TABLE recurring_availabilities (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL
                        REFERENCES users(id),
                    weekday INTEGER NOT NULL,
                    start_time TIME NOT NULL,
                    end_time TIME NOT NULL,
                    active BOOLEAN NOT NULL DEFAULT 1,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL
                )
                """
            )
        )

        connection.execute(
            text(
                """
                CREATE INDEX
                ix_recurring_availabilities_user_id
                ON recurring_availabilities(user_id)
                """
            )
        )

    print(
        "Created table recurring_availabilities."
    )


if __name__ == "__main__":
    migrate()