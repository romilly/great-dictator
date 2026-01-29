from io import BytesIO
from pathlib import Path

import pytest
from hamcrest import assert_that, contains_string

from great_dictator.adapters.outbound.whisper_transcriber import WhisperTranscriber


@pytest.fixture(scope="module")
def whisper_transcriber():
    return WhisperTranscriber(model_size="tiny")


@pytest.fixture
def test_audio_bytes():
    audio_path = Path(__file__).parent.parent / "data" / "test_audio.wav"
    return BytesIO(audio_path.read_bytes())


def test_transcriber_returns_text_from_audio(whisper_transcriber, test_audio_bytes):
    result = whisper_transcriber.transcribe(test_audio_bytes)

    assert_that(result.text.lower(), contains_string("hello"))
