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


def test_transcribe_returns_html_fragment(client, fake_transcriber):
    audio_content = b"fake audio data"
    files = {"audio": ("test.webm", audio_content, "audio/webm")}

    response = client.post("/transcribe", files=files)

    assert_that(response.status_code, equal_to(200))
    assert_that(response.text, contains_string("fake transcription"))
    assert fake_transcriber.last_audio is not None
