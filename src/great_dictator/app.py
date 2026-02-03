import os
from pathlib import Path

from dotenv import load_dotenv

from great_dictator.adapters.inbound.fastapi_app import create_app
from great_dictator.adapters.outbound.sqlite_document_repository import (
    SqliteDocumentRepository,
)
from great_dictator.adapters.outbound.whisper_transcriber import WhisperTranscriber
from great_dictator.domain.transcription import TranscriptionService

load_dotenv()

db_path = os.getenv("DATABASE_PATH", "data/documents.db")
db_dir = Path(db_path).parent
db_dir.mkdir(parents=True, exist_ok=True)

transcriber = WhisperTranscriber(
    model_size="base",
    device="cpu",
    compute_type="int8",
)
service = TranscriptionService(transcriber)
document_repository = SqliteDocumentRepository(db_path)
app = create_app(service, document_repository, on_shutdown=transcriber.close)
