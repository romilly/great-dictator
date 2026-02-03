import pytest
from hamcrest import assert_that, contains_string, equal_to
from starlette.testclient import TestClient

from great_dictator.adapters.inbound.fastapi_app import create_app
from great_dictator.domain.transcription import TranscriptionService


@pytest.fixture
def app(fake_transcriber):
    service = TranscriptionService(fake_transcriber)
    return create_app(service)


@pytest.fixture
def client(app):
    return TestClient(app)


def test_index_returns_html_page(client):
    response = client.get("/")

    assert_that(response.status_code, equal_to(200))
    assert_that(response.text, contains_string("<html"))


def test_transcribe_returns_text(client, fake_transcriber):
    """Basic transcribe endpoint returns plain text."""
    audio_content = b"fake audio data"
    files = {"audio": ("test.webm", audio_content, "audio/webm")}

    response = client.post("/transcribe", files=files)

    assert_that(response.status_code, equal_to(200))
    assert_that(response.text, contains_string("fake transcription"))
    assert fake_transcriber.last_audio is not None


def test_transcribe_htmx_returns_editor_fragment(client, fake_transcriber):
    """Transcribe with htmx header returns editor fragment with transcription."""
    audio_content = b"fake audio data"
    files = {"audio": ("test.webm", audio_content, "audio/webm")}
    # Add current content to be preserved/appended to
    data = {"existingContent": "Previous text. "}

    response = client.post(
        "/transcribe",
        files=files,
        data=data,
        headers={"HX-Request": "true"},
    )

    assert_that(response.status_code, equal_to(200))
    # Should return editor fragment with combined content
    assert_that(response.text, contains_string("Previous text."))
    assert_that(response.text, contains_string("fake transcription"))
    assert_that(response.text, contains_string('id="transcription"'))


def test_transcribe_htmx_preserves_document_name(client, fake_transcriber):
    """Transcribe with htmx preserves document name and id in returned fragment."""
    audio_content = b"fake audio data"
    files = {"audio": ("test.webm", audio_content, "audio/webm")}
    data = {
        "existingContent": "Some text. ",
        "documentName": "My Meeting Notes",
        "documentId": "42",
    }

    response = client.post(
        "/transcribe",
        files=files,
        data=data,
        headers={"HX-Request": "true"},
    )

    assert_that(response.status_code, equal_to(200))
    # Document name should be preserved in the input field
    assert_that(response.text, contains_string('value="My Meeting Notes"'))
    # Document ID should be preserved in the hidden field
    assert_that(response.text, contains_string('value="42"'))
