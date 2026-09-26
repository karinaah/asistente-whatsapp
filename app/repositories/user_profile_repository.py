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

    def update_work_duration_multiplier(
        self,
        db: Session,
        user_id: int,
        multiplier: float,
    ) -> UserProfileDB | None:
        profile = self.get_by_user_id(
            db,
            user_id=user_id,
        )

        if profile is None:
            return None

        profile.work_duration_multiplier = multiplier

        db.commit()
        db.refresh(profile)

        return profile    