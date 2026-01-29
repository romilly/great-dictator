from io import BytesIO

from hamcrest import assert_that, equal_to

from great_dictator.domain.transcription import (
    TranscriberPort,
    TranscriptionResult,
    TranscriptionService,
)


class FakeTranscriber(TranscriberPort):
    def __init__(self, result: TranscriptionResult):
        self._result = result

    def transcribe(self, audio: BytesIO) -> TranscriptionResult:
        return self._result


def test_service_delegates_to_transcriber():
    expected_result = TranscriptionResult(text="hello world", language="en")
    fake_transcriber = FakeTranscriber(expected_result)
    service = TranscriptionService(fake_transcriber)

    audio = BytesIO(b"fake audio data")
    result = service.transcribe(audio)

    assert_that(result, equal_to(expected_result))
