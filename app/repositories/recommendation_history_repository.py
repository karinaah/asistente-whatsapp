import json

from sqlalchemy.orm import Session

from app.models.human_state import HumanState
from app.models.recommendation import Recommendation
from app.models.recommendation_history_db import (
    RecommendationHistoryDB,
)


class RecommendationHistoryRepository:
    def save(
        self,
        db: Session,
        recommendation: Recommendation,
        human_state: HumanState | None,
    ) -> RecommendationHistoryDB:
        reasons_json = json.dumps(
            [
                {
                    "code": reason.code.value,
                    "message": reason.message,
                    "score": reason.score,
                }
                for reason in recommendation.reasons
            ],
            ensure_ascii=False,
        )

        history_db = RecommendationHistoryDB(
            task_id=recommendation.task.id,
            task_title=recommendation.task.title,
            score=recommendation.score,
            summary=recommendation.summary,
            reasons_json=reasons_json,
            energy=(
                human_state.energy.value
                if human_state and human_state.energy
                else None
            ),
            focus=(
                human_state.focus.value
                if human_state and human_state.focus
                else None
            ),
            stress=(
                human_state.stress.value
                if human_state and human_state.stress
                else None
            ),
            available_minutes=(
                human_state.available_minutes
                if human_state
                else None
            ),
        )

        db.add(history_db)
        db.commit()
        db.refresh(history_db)

        return history_db

    def get_all(
        self,
        db: Session,
    ) -> list[RecommendationHistoryDB]:
        return (
            db.query(RecommendationHistoryDB)
            .order_by(
                RecommendationHistoryDB.created_at.desc()
            )
            .all()
        )