import os
from io import BytesIO
from pathlib import Path
from typing import Generator

import pytest
from dotenv import load_dotenv

from great_dictator.adapters.outbound.sqlite_document_repository import (
    SqliteDocumentRepository,
)
from great_dictator.domain.transcription import TranscriberPort, TranscriptionResult


class FakeTranscriber(TranscriberPort):
    def __init__(self, result: TranscriptionResult | None = None):
        self._result = result or TranscriptionResult(text="fake transcription", language="en")
        self.last_audio: BytesIO | None = None

    def transcribe(self, audio: BytesIO) -> TranscriptionResult:
        self.last_audio = audio
        return self._result


@pytest.fixture
def fake_transcriber() -> FakeTranscriber:
    return FakeTranscriber()


@pytest.fixture
def db_repository() -> Generator[SqliteDocumentRepository, None, None]:
    load_dotenv(dotenv_path=Path(__file__).parent / ".env")
    db_path = os.getenv("DATABASE_PATH")
    assert db_path is not None, "DATABASE_PATH not set in tests/.env"

    # Ensure the database directory exists
    db_dir = Path(db_path).parent
    db_dir.mkdir(parents=True, exist_ok=True)

    repo = SqliteDocumentRepository(db_path)
    # DELETE rows (not DROP tables) - documents has no FKs currently
    with repo._get_connection() as conn:
        conn.execute("DELETE FROM documents")
        conn.commit()
    yield repo
    # Leave data for debugging after tests
