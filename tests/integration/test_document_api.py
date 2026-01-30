from datetime import datetime

import pytest
from hamcrest import assert_that, equal_to, has_item, has_length
from starlette.testclient import TestClient

from great_dictator.adapters.inbound.fastapi_app import create_app
from great_dictator.domain.document import Document
from great_dictator.domain.transcription import TranscriptionService
from tests.fakes.fake_document_repository import FakeDocumentRepository


@pytest.fixture
def document_repository():
    return FakeDocumentRepository()


@pytest.fixture
def app(fake_transcriber, document_repository):
    service = TranscriptionService(fake_transcriber)
    return create_app(service, document_repository)


@pytest.fixture
def client(app):
    return TestClient(app)


def test_post_documents_returns_201_with_id(client):
    response = client.post(
        "/documents",
        json={
            "user": "romilly",
            "name": "my doc",
            "content": "hello world",
        },
    )

    assert_that(response.status_code, equal_to(201))
    data = response.json()
    assert "id" in data
    assert_that(data["name"], equal_to("my doc"))


def test_get_documents_returns_users_documents(client, document_repository):
    doc = Document(
        user="romilly",
        name="existing doc",
        content="content",
        created=datetime(2024, 1, 15, 10, 30),
    )
    document_repository.save(doc)

    response = client.get("/documents?user=romilly")

    assert_that(response.status_code, equal_to(200))
    data = response.json()
    assert_that(data, has_length(1))
    assert_that(data[0]["name"], equal_to("existing doc"))


def test_get_document_by_id_returns_document(client, document_repository):
    doc = Document(
        user="romilly",
        name="test doc",
        content="hello world",
        created=datetime(2024, 1, 15, 10, 30),
    )
    saved = document_repository.save(doc)

    response = client.get(f"/documents/{saved.id}")

    assert_that(response.status_code, equal_to(200))
    data = response.json()
    assert_that(data["name"], equal_to("test doc"))
    assert_that(data["content"], equal_to("hello world"))


def test_get_document_by_id_returns_404_for_missing(client):
    response = client.get("/documents/999")

    assert_that(response.status_code, equal_to(404))


def test_put_document_updates_document(client, document_repository):
    doc = Document(
        user="romilly",
        name="test doc",
        content="original content",
        created=datetime(2024, 1, 15, 10, 30),
    )
    saved = document_repository.save(doc)

    response = client.put(
        f"/documents/{saved.id}",
        json={
            "user": "romilly",
            "name": "test doc",
            "content": "updated content",
        },
    )

    assert_that(response.status_code, equal_to(200))
    data = response.json()
    assert_that(data["content"], equal_to("updated content"))


def test_put_document_returns_404_for_missing(client):
    response = client.put(
        "/documents/999",
        json={
            "user": "romilly",
            "name": "test doc",
            "content": "content",
        },
    )

    assert_that(response.status_code, equal_to(404))


def test_delete_document_removes_document(client, document_repository):
    doc = Document(
        user="romilly",
        name="test doc",
        content="hello world",
        created=datetime(2024, 1, 15, 10, 30),
    )
    saved = document_repository.save(doc)

    response = client.delete(f"/documents/{saved.id}")

    assert_that(response.status_code, equal_to(204))
    assert document_repository.load(saved.id) is None  # type: ignore[arg-type]


def test_delete_document_returns_404_for_missing(client):
    response = client.delete("/documents/999")

    assert_that(response.status_code, equal_to(404))
