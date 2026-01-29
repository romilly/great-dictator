from great_dictator.adapters.inbound.fastapi_app import create_app
from great_dictator.adapters.outbound.whisper_transcriber import WhisperTranscriber
from great_dictator.domain.transcription import TranscriptionService

transcriber = WhisperTranscriber(model_size="base")
service = TranscriptionService(transcriber)
app = create_app(service)
