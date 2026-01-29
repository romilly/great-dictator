from io import BytesIO

import pytest

from great_dictator.domain.transcription import TranscriberPort, TranscriptionResult


class FakeTranscriber(TranscriberPort):
    def __init__(self, result: TranscriptionResult | None = None):
        self._result = result or TranscriptionResult(text="fake transcription", language="en")
        self.last_audio: BytesIO | None = None

    def transcribe(self, audio: BytesIO) -> TranscriptionResult:
        self.last_audio = audio
        return self._result


@pytest.fixture
def fake_transcriber():
    return FakeTranscriber()
