from sqlalchemy import inspect, text

from app.config.database import engine


TABLE_NAME = "notifications"


def table_exists() -> bool:
    inspector = inspect(engine)

    return TABLE_NAME in inspector.get_table_names()


def migrate():
    if table_exists():
        print(
            "Migration skipped: "
            "notifications already exists."
        )
        return

    with engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE TABLE notifications (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    follow_up_id INTEGER,
                    title VARCHAR(200) NOT NULL,
                    message VARCHAR(1000) NOT NULL,
                    channel VARCHAR(30) NOT NULL,
                    status VARCHAR(30) NOT NULL,
                    created_at DATETIME NOT NULL,
                    delivered_at DATETIME,
                    read_at DATETIME,
                    FOREIGN KEY(user_id)
                        REFERENCES users(id),
                    FOREIGN KEY(follow_up_id)
                        REFERENCES proactive_follow_ups(id)
                )
                """
            )
        )

        connection.execute(
            text(
                """
                CREATE INDEX
                ix_notifications_user_id
                ON notifications(user_id)
                """
            )
        )

        connection.execute(
            text(
                """
                CREATE INDEX
                ix_notifications_follow_up_id
                ON notifications(follow_up_id)
                """
            )
        )

    print(
        "Migration completed: "
        "notifications created."
    )


if __name__ == "__main__":
    migrate()