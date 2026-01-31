import pytest
from hamcrest import assert_that, contains_exactly
from starlette.testclient import TestClient

from great_dictator.adapters.inbound.fastapi_app import create_app
from great_dictator.domain.transcription import TranscriptionService
from tests.builders import a_document
from tests.fakes.fake_document_repository import FakeDocumentRepository
from tests.matchers import (
    document_response,
    is_created_with,
    is_no_content,
    is_not_found,
    is_ok_with,
)


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

    assert_that(response, is_created_with(document_response(name="my doc", has_id=True)))


def test_get_documents_returns_users_documents(client, document_repository):
    doc = a_document().with_name("existing doc").build()
    document_repository.save(doc)

    response = client.get("/documents?user=romilly")

    assert_that(response, is_ok_with(contains_exactly(document_response(name="existing doc"))))


def test_get_document_by_id_returns_document(client, document_repository):
    doc = a_document().with_name("test doc").with_content("hello world").build()
    saved = document_repository.save(doc)

    response = client.get(f"/documents/{saved.id}")

    assert_that(response, is_ok_with(document_response(name="test doc", content="hello world")))


def test_get_document_by_id_returns_404_for_missing(client):
    response = client.get("/documents/999")

    assert_that(response, is_not_found())


def test_put_document_updates_document(client, document_repository):
    doc = a_document().with_name("test doc").with_content("original content").build()
    saved = document_repository.save(doc)

    response = client.put(
        f"/documents/{saved.id}",
        json={
            "user": "romilly",
            "name": "test doc",
            "content": "updated content",
        },
    )

    assert_that(response, is_ok_with(document_response(content="updated content")))


def test_put_document_returns_404_for_missing(client):
    response = client.put(
        "/documents/999",
        json={
            "user": "romilly",
            "name": "test doc",
            "content": "content",
        },
    )

    assert_that(response, is_not_found())


def test_delete_document_removes_document(client, document_repository):
    doc = a_document().with_name("test doc").with_content("hello world").build()
    saved = document_repository.save(doc)

    response = client.delete(f"/documents/{saved.id}")

    assert_that(response, is_no_content())
    assert document_repository.load(saved.id) is None  # type: ignore[arg-type]


def test_delete_document_returns_404_for_missing(client):
    response = client.delete("/documents/999")

    assert_that(response, is_not_found())
