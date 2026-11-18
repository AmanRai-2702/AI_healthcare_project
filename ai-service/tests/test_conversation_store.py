
import pytest

from app.common import conversation_store as store


@pytest.fixture
def test_db(tmp_path, monkeypatch):
    """Use a temporary database for every test."""

    monkeypatch.setattr(
        store,
        "DB_PATH",
        tmp_path / "test_conversations.db",
    )

    store.init_db()


def test_create_conversation(test_db):
    conversation_id = store.create_conversation("patient-001")

    assert isinstance(conversation_id, str)
    assert len(conversation_id) > 0

    assert store.validate_conversation(
        conversation_id,
        "patient-001",
    )


def test_save_and_retrieve_messages(test_db):
    conversation_id = store.create_conversation("patient-001")

    store.save_message(
        conversation_id,
        "patient-001",
        "user",
        "What is my hemoglobin level?",
    )

    store.save_message(
        conversation_id,
        "patient-001",
        "assistant",
        "Your report shows 13.5 g/dL.",
    )

    history = store.get_conversation_history(
        conversation_id,
        "patient-001",
    )

    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"
    assert "13.5" in history[1]["content"]


def test_patient_cannot_access_another_patients_conversation(test_db):
    conversation_id = store.create_conversation("patient-001")

    store.save_message(
        conversation_id,
        "patient-001",
        "user",
        "My medical question",
    )

    assert not store.validate_conversation(
        conversation_id,
        "patient-002",
    )

    with pytest.raises(ValueError):
        store.get_conversation_history(
            conversation_id,
            "patient-002",
        )


def test_invalid_message_role_is_rejected(test_db):
    conversation_id = store.create_conversation("patient-001")

    with pytest.raises(ValueError):
        store.save_message(
            conversation_id,
            "patient-001",
            "system",
            "Invalid message",
        )


def test_conversation_history_is_persistent(test_db):
    conversation_id = store.create_conversation("patient-001")

    store.save_message(
        conversation_id,
        "patient-001",
        "user",
        "Remember my previous question.",
    )

    # Read again through a new database connection.
    history = store.get_conversation_history(
        conversation_id,
        "patient-001",
    )

    assert len(history) == 1
    assert history[0]["content"] == "Remember my previous question."
