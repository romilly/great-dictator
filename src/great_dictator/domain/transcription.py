from abc import ABC, abstractmethod
from dataclasses import dataclass
from io import BytesIO


@dataclass(frozen=True)
class TranscriptionResult:
    text: str
    language: str


class TranscriberPort(ABC):
    @abstractmethod
    def transcribe(self, audio: BytesIO) -> TranscriptionResult:
        pass


class TranscriptionService:
    def __init__(self, transcriber: TranscriberPort):
        self._transcriber = transcriber

    def transcribe(self, audio: BytesIO) -> TranscriptionResult:
        return self._transcriber.transcribe(audio)
