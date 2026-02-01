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


def test_transcriber_serializes_concurrent_calls(whisper_transcriber, test_audio_bytes):
    """Verify that concurrent transcribe calls are serialized (not processed simultaneously).

    If calls are serialized, two concurrent calls should take roughly 2x a single call.
    If they run in parallel, two concurrent calls would take roughly 1x a single call.
    """
    import threading
    import time

    # First, time a single transcription call to get baseline
    audio = BytesIO(test_audio_bytes.getvalue())
    single_start = time.monotonic()
    whisper_transcriber.transcribe(audio)
    single_call_time = time.monotonic() - single_start

    # Now make two concurrent calls
    def transcribe_once():
        audio = BytesIO(test_audio_bytes.getvalue())
        whisper_transcriber.transcribe(audio)

    threads = [threading.Thread(target=transcribe_once) for _ in range(2)]
    concurrent_start = time.monotonic()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    concurrent_time = time.monotonic() - concurrent_start

    # If serialized, concurrent time should be at least 1.5x single call time
    # (allowing some margin for thread overhead)
    assert concurrent_time >= single_call_time * 1.5, (
        f"Calls may have run in parallel: concurrent={concurrent_time:.3f}s, "
        f"single={single_call_time:.3f}s, ratio={concurrent_time/single_call_time:.2f}"
    )
