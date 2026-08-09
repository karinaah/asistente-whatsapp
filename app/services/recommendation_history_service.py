from sqlalchemy.orm import Session

from app.models.human_state import HumanState
from app.models.recommendation import Recommendation
from app.models.recommendation_history import (
    RecommendationHistory,
)
from app.models.recommendation_history_db import (
    RecommendationHistoryDB,
)
from app.repositories.recommendation_history_repository import (
    RecommendationHistoryRepository,
)


class RecommendationHistoryService:
    def __init__(self) -> None:
        self.repository = RecommendationHistoryRepository()

    def save(
        self,
        db: Session,
        recommendation: Recommendation,
        human_state: HumanState | None,
    ) -> RecommendationHistoryDB:
        return self.repository.save(
            db=db,
            recommendation=recommendation,
            human_state=human_state,
        )

    def get_all(
        self,
        db: Session,
    ) -> list[RecommendationHistory]:
        history = self.repository.get_all(db)

        return [
            RecommendationHistory.model_validate(item)
            for item in history
        ]
    
    def get_latest(
        self,
        db: Session,
    ) -> RecommendationHistory | None:
        history = self.repository.get_latest(db)

        if history is None:
            return None

        return RecommendationHistory.model_validate(
            history
        )    