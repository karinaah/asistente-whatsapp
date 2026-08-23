from app.services.mock_ai_service import MockAIService


def test_extracts_clean_title_for_urgent_meeting():
    service = MockAIService()

    tasks = service.extract_tasks(
        "Me apareció una reunión urgente de 45 minutos"
    )

    assert len(tasks) == 1
    assert tasks[0].title == "Reunión urgente"
    assert tasks[0].estimated_minutes == 45