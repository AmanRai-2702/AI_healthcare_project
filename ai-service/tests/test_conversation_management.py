
import pytest

from app.common import conversation_store as store


@pytest.fixture
def test_db(tmp_path, monkeypatch):
    monkeypatch.setattr(
        store,
        "DB_PATH",
        tmp_path / "test_conversations.db",
    )
    store.init_db()


def test_list_conversations(test_db):
    conversation_id = store.create_conversation("patient-001")

    store.save_message(
        conversation_id,
        "patient-001",
        "user",
        "What is my hemoglobin?",
    )

    conversations = store.list_conversations("patient-001")

    assert len(conversations) == 1
    assert conversations[0]["conversation_id"] == conversation_id
    assert conversations[0]["message_count"] == 1
    assert conversations[0]["last_message"] == "What is my hemoglobin?"


def test_list_conversations_does_not_return_other_patients(test_db):
    store.create_conversation("patient-001")
    store.create_conversation("patient-002")

    conversations = store.list_conversations("patient-001")

    assert len(conversations) == 1


def test_delete_conversation(test_db):
    conversation_id = store.create_conversation("patient-001")

    store.save_message(
        conversation_id,
        "patient-001",
        "user",
        "Hello",
    )

    deleted = store.delete_conversation(
        conversation_id,
        "patient-001",
    )

    assert deleted is True
    assert store.validate_conversation(
        conversation_id,
        "patient-001",
    ) is False


def test_patient_cannot_delete_another_patients_conversation(test_db):
    conversation_id = store.create_conversation("patient-001")

    deleted = store.delete_conversation(
        conversation_id,
        "patient-002",
    )

    assert deleted is False
    assert store.validate_conversation(
        conversation_id,
        "patient-001",
    ) is True


def test_deleting_conversation_also_deletes_messages(test_db):
    conversation_id = store.create_conversation("patient-001")

    store.save_message(
        conversation_id,
        "patient-001",
        "user",
        "Hello",
    )

    store.delete_conversation(
        conversation_id,
        "patient-001",
    )

    with store.get_connection() as connection:
        result = connection.execute(
            """
            SELECT COUNT(*)
            FROM messages
            WHERE conversation_id = ?
            """,
            (conversation_id,),
        ).fetchone()

    assert result[0] == 0
