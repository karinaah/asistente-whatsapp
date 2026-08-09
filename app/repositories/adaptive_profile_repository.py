from sqlalchemy.orm import Session

from app.models.adaptive_profile import AdaptiveProfile
from app.models.adaptive_profile_db import (
    AdaptiveProfileDB,
)


class AdaptiveProfileRepository:
    def get(
        self,
        db: Session,
    ) -> AdaptiveProfileDB | None:
        return (
            db.query(AdaptiveProfileDB)
            .order_by(AdaptiveProfileDB.id.desc())
            .first()
        )

    def save(
        self,
        db: Session,
        profile: AdaptiveProfile,
    ) -> AdaptiveProfileDB:
        existing = self.get(db)

        if existing is None:
            entity = AdaptiveProfileDB(
                **profile.model_dump()
            )

            db.add(entity)

        else:
            for field, value in (
                profile.model_dump().items()
            ):
                setattr(
                    existing,
                    field,
                    value,
                )

            entity = existing

        db.commit()
        db.refresh(entity)

        return entity