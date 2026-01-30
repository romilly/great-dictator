from pathlib import Path

from great_dictator.adapters.inbound.fastapi_app import create_app
from great_dictator.adapters.outbound.sqlite_document_repository import (
    SqliteDocumentRepository,
)
from great_dictator.adapters.outbound.whisper_transcriber import WhisperTranscriber
from great_dictator.domain.transcription import TranscriptionService

# Create data directory if it doesn't exist
data_dir = Path.home() / ".great-dictator"
data_dir.mkdir(exist_ok=True)

transcriber = WhisperTranscriber(model_size="base")
service = TranscriptionService(transcriber)
document_repository = SqliteDocumentRepository(str(data_dir / "documents.db"))
app = create_app(service, document_repository)
