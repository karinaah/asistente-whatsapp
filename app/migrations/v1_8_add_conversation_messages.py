from sqlalchemy import inspect

from app.config.database import engine
from app.models.user_db import UserDB
from app.models.conversation_message_db import ConversationMessageDB


def migrate() -> None:
    inspector = inspect(engine)

    if "conversation_messages" in inspector.get_table_names():
        return

    ConversationMessageDB.__table__.create(
        bind=engine,
        checkfirst=True,
    )


if __name__ == "__main__":
    migrate()