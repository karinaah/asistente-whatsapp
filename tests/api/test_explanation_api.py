from fastapi.testclient import TestClient

from app.main import app
from app.api import explanation_api


client = TestClient(app)


def test_explain_learning_uses_user_id(
    monkeypatch,
):
    captured_user_ids = []

    def fake_get_all_for_learning(
        db,
        user_id=None,
    ):
        captured_user_ids.append(user_id)
        return []

    monkeypatch.setattr(
        explanation_api.task_execution_service,
        "get_all_for_learning",
        fake_get_all_for_learning,
    )

    response = client.get(
        "/explanations/learning?user_id=123"
    )

    assert response.status_code == 200
    assert captured_user_ids == [123]

def test_explain_learning_without_user_id(
    monkeypatch,
):
    captured_user_ids = []

    def fake_get_all_for_learning(
        db,
        user_id=None,
    ):
        captured_user_ids.append(user_id)
        return []

    monkeypatch.setattr(
        explanation_api.task_execution_service,
        "get_all_for_learning",
        fake_get_all_for_learning,
    )

    response = client.get(
        "/explanations/learning"
    )

    assert response.status_code == 200
    assert captured_user_ids == [None]    