from io import BytesIO
from pathlib import Path

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, HTMLResponse

from great_dictator.domain.transcription import TranscriptionService

STATIC_DIR = Path(__file__).parent.parent.parent / "static"


def create_app(transcription_service: TranscriptionService) -> FastAPI:
    app = FastAPI()

    @app.get("/", response_class=HTMLResponse)
    async def index():
        return FileResponse(STATIC_DIR / "index.html")

    @app.post("/transcribe", response_class=HTMLResponse)
    async def transcribe(audio: UploadFile = File(...)):
        audio_bytes = await audio.read()
        result = transcription_service.transcribe(BytesIO(audio_bytes))
        return result.text

    return app
