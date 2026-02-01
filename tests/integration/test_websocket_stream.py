"""Tests for WebSocket streaming transcription endpoint."""
import pytest
from hamcrest import assert_that, equal_to
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


def test_websocket_stream_sends_ready_on_connect(client):
    """WebSocket connection sends ready message on connect."""
    with client.websocket_connect("/api/stream") as websocket:
        data = websocket.receive_json()

    assert_that(data, equal_to({"type": "ready"}))


def test_websocket_stream_transcribes_audio(client, fake_transcriber):
    """WebSocket transcribes audio and returns result."""
    # PCM audio: 16-bit samples at 16kHz, mono
    # 3200 bytes = 100ms of audio (16000 samples/sec * 2 bytes/sample * 0.1 sec)
    audio_chunk = b"\x00\x01" * 1600

    with client.websocket_connect("/api/stream") as websocket:
        ready = websocket.receive_json()
        assert_that(ready["type"], equal_to("ready"))

        # Send audio chunk
        websocket.send_bytes(audio_chunk)

        # Request transcription by sending end-of-speech signal
        websocket.send_json({"type": "end_of_speech"})

        # Should receive transcription result
        result = websocket.receive_json()

    assert_that(result["type"], equal_to("final"))
    assert_that(result["text"], equal_to("fake transcription"))
