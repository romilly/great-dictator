from io import BytesIO

from faster_whisper import WhisperModel

from great_dictator.domain.transcription import TranscriberPort, TranscriptionResult


class WhisperTranscriber(TranscriberPort):
    def __init__(self, model_size: str = "base"):
        self._model = WhisperModel(model_size, device="cpu", compute_type="int8")

    def transcribe(self, audio: BytesIO) -> TranscriptionResult:
        segments, info = self._model.transcribe(audio)
        text = " ".join(segment.text.strip() for segment in segments)
        return TranscriptionResult(text=text, language=info.language)
