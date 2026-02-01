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


def test_api_transcribe_returns_json(client, fake_transcriber):
    """POST /api/transcribe with raw WAV bytes returns JSON with text."""
    audio_content = b"fake wav audio data"

    response = client.post(
        "/api/transcribe",
        content=audio_content,
        headers={"Content-Type": "audio/wav"},
    )

    assert_that(response.status_code, equal_to(200))
    assert_that(response.headers["content-type"], contains_string("application/json"))
    assert_that(response.json(), equal_to({"text": "fake transcription"}))


def test_api_transcribe_returns_400_for_invalid_content_type(client):
    """POST /api/transcribe without audio/wav content-type returns 400."""
    audio_content = b"fake audio data"

    response = client.post(
        "/api/transcribe",
        content=audio_content,
        headers={"Content-Type": "application/json"},
    )

    assert_that(response.status_code, equal_to(400))
