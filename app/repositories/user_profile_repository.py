from sqlalchemy.orm import Session

from app.models.user_profile_db import UserProfileDB


class UserProfileRepository:
    def create(
        self,
        db: Session,
        user_id: int,
    ) -> UserProfileDB:
        profile = UserProfileDB(
            user_id=user_id,
        )

        db.add(profile)
        db.commit()
        db.refresh(profile)

        return profile

    def get_by_user_id(
        self,
        db: Session,
        user_id: int,
    ) -> UserProfileDB | None:
        return (
            db.query(UserProfileDB)
            .filter(
                UserProfileDB.user_id == user_id
            )
            .first()
        )