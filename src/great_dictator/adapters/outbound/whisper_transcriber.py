import gc
import threading
from io import BytesIO

from faster_whisper import WhisperModel

from great_dictator.domain.transcription import TranscriberPort, TranscriptionResult


class WhisperTranscriber(TranscriberPort):
    def __init__(
        self,
        model_size: str = "base",
        device: str = "cpu",
        compute_type: str = "int8",
    ):
        self._model: WhisperModel | None = WhisperModel(
            model_size, device=device, compute_type=compute_type
        )
        self._lock = threading.Lock()

    def transcribe(self, audio: BytesIO) -> TranscriptionResult:
        if self._model is None:
            raise RuntimeError("Transcriber has been closed")
        with self._lock:
            segments, info = self._model.transcribe(audio)
            text = " ".join(segment.text.strip() for segment in segments)
        return TranscriptionResult(text=text, language=info.language)

    def close(self) -> None:
        """Release the Whisper model to free resources."""
        if self._model is not None:
            del self._model
            self._model = None
            gc.collect()
