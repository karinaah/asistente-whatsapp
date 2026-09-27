from sqlalchemy import inspect, text

from app.config.database import engine


TABLE_NAME = "proactive_follow_ups"


def table_exists() -> bool:
    inspector = inspect(engine)

    return TABLE_NAME in inspector.get_table_names()


def migrate():
    if table_exists():
        print(
            "Migration skipped: "
            "proactive_follow_ups already exists."
        )
        return

    with engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE TABLE proactive_follow_ups (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    follow_up_type VARCHAR(50) NOT NULL,
                    title VARCHAR(200) NOT NULL,
                    message VARCHAR(1000) NOT NULL,
                    task_id INTEGER,
                    routine_id INTEGER,
                    status VARCHAR(30) NOT NULL,
                    created_at DATETIME NOT NULL,
                    resolved_at DATETIME,
                    FOREIGN KEY(user_id)
                        REFERENCES users(id),
                    FOREIGN KEY(task_id)
                        REFERENCES tasks(id),
                    FOREIGN KEY(routine_id)
                        REFERENCES routines(id)
                )
                """
            )
        )

        connection.execute(
            text(
                """
                CREATE INDEX
                ix_proactive_follow_ups_user_id
                ON proactive_follow_ups(user_id)
                """
            )
        )

        connection.execute(
            text(
                """
                CREATE INDEX
                ix_proactive_follow_ups_task_id
                ON proactive_follow_ups(task_id)
                """
            )
        )

        connection.execute(
            text(
                """
                CREATE INDEX
                ix_proactive_follow_ups_routine_id
                ON proactive_follow_ups(routine_id)
                """
            )
        )

    print(
        "Migration completed: "
        "proactive_follow_ups created."
    )


if __name__ == "__main__":
    migrate()