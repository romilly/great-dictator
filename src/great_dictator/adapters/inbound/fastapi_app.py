from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Callable, Optional

try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated

from fastapi import FastAPI, File, Form, Header, HTTPException, Request, UploadFile, WebSocket
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from pydantic import BaseModel

from great_dictator.adapters.inbound.templates import render_document_list, render_editor
from great_dictator.domain.document import Document, DocumentRepositoryPort
from great_dictator.domain.transcription import TranscriptionService

STATIC_DIR = Path(__file__).parent.parent.parent / "static"

# Audio constants for PCM to WAV conversion
SAMPLE_RATE = 16000
CHANNELS = 1
SAMPLE_WIDTH = 2  # 16-bit


def _pcm_to_wav(pcm_data: bytes) -> bytes:
    """Convert raw PCM audio to WAV format."""
    import struct
    import wave

    output = BytesIO()
    with wave.open(output, "wb") as wav_file:
        wav_file.setnchannels(CHANNELS)
        wav_file.setsampwidth(SAMPLE_WIDTH)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(pcm_data)
    return output.getvalue()


class DocumentCreateRequest(BaseModel):
    user: str
    name: str
    content: str


class DocumentUpdateRequest(BaseModel):
    user: str
    name: str
    content: str


class DocumentResponse(BaseModel):
    id: int
    user: str
    name: str
    content: str
    created: datetime


class DocumentSummaryResponse(BaseModel):
    id: int
    name: str
    created: datetime


def create_app(
    transcription_service: TranscriptionService,
    document_repository: Optional[DocumentRepositoryPort] = None,
    on_shutdown: Optional[Callable[[], None]] = None,
) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        # Warmup: force model into memory before accepting requests
        try:
            transcription_service.transcribe(BytesIO(b""))
        except Exception:
            pass  # Empty audio fails, but model is now loaded
        yield
        if on_shutdown is not None:
            on_shutdown()

    app = FastAPI(lifespan=lifespan)

    @app.get("/", response_class=HTMLResponse)
    async def index() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    @app.post("/transcribe", response_class=HTMLResponse)
    async def transcribe(
        audio: UploadFile = File(...),
        existingContent: Annotated[str, Form()] = "",
        hx_request: Annotated[Optional[str], Header(alias="HX-Request")] = None,
    ) -> str:
        audio_bytes = await audio.read()
        result = transcription_service.transcribe(BytesIO(audio_bytes))

        # If htmx request, return editor fragment with combined content
        if hx_request:
            combined_content = existingContent + result.text
            return render_editor(content=combined_content, status="Transcribed")

        # Otherwise return just the text (backward compatible)
        return result.text

    @app.post("/api/transcribe")
    async def api_transcribe(request: Request) -> JSONResponse:
        content_type = request.headers.get("content-type", "")
        if not content_type.startswith("audio/wav"):
            raise HTTPException(status_code=400, detail="Content-Type must be audio/wav")
        audio_bytes = await request.body()
        try:
            result = transcription_service.transcribe(BytesIO(audio_bytes))
        except RuntimeError:
            raise HTTPException(status_code=503, detail="Transcriber unavailable")
        return JSONResponse(content={"text": result.text})

    @app.websocket("/api/stream")
    async def stream_transcribe(websocket: WebSocket) -> None:
        await websocket.accept()
        await websocket.send_json({"type": "ready"})

        audio_buffer = bytearray()

        try:
            while True:
                message = await websocket.receive()

                if message["type"] == "websocket.disconnect":
                    break

                if "bytes" in message:
                    audio_buffer.extend(message["bytes"])

                elif "text" in message:
                    import json
                    data = json.loads(message["text"])

                    if data.get("type") == "end_of_speech" and audio_buffer:
                        # Convert PCM to WAV for transcription
                        wav_audio = _pcm_to_wav(bytes(audio_buffer))
                        result = transcription_service.transcribe(BytesIO(wav_audio))
                        await websocket.send_json({
                            "type": "final",
                            "text": result.text,
                        })
                        audio_buffer.clear()

        except Exception as e:
            try:
                await websocket.send_json({"type": "error", "message": str(e)})
            except Exception:
                pass

    if document_repository is not None:
        @app.post("/documents", status_code=201, response_model=DocumentResponse)
        async def create_document(request: DocumentCreateRequest) -> DocumentResponse:
            doc = Document(
                user=request.user,
                name=request.name,
                content=request.content,
                created=datetime.now(),
            )
            saved = document_repository.save(doc)
            return DocumentResponse(
                id=saved.id,  # type: ignore[arg-type]
                user=saved.user,
                name=saved.name,
                content=saved.content,
                created=saved.created,
            )

        @app.get("/documents", response_model=list[DocumentSummaryResponse])
        async def list_documents(user: str) -> list[DocumentSummaryResponse]:
            summaries = document_repository.list_for_user(user)
            return [
                DocumentSummaryResponse(id=s.id, name=s.name, created=s.created)
                for s in summaries
            ]

        @app.get("/documents/list-html", response_class=HTMLResponse)
        async def documents_list_html(user: str) -> str:
            summaries = document_repository.list_for_user(user)
            documents = [(s.id, s.name, s.created) for s in summaries]
            return render_document_list(documents)

        @app.get("/documents/{document_id}", response_model=DocumentResponse)
        async def get_document(document_id: int) -> DocumentResponse:
            doc = document_repository.load(document_id)
            if doc is None:
                raise HTTPException(status_code=404, detail="Document not found")
            return DocumentResponse(
                id=doc.id,  # type: ignore[arg-type]
                user=doc.user,
                name=doc.name,
                content=doc.content,
                created=doc.created,
            )

        @app.put("/documents/{document_id}", response_model=DocumentResponse)
        async def update_document(
            document_id: int, request: DocumentUpdateRequest
        ) -> DocumentResponse:
            existing = document_repository.load(document_id)
            if existing is None:
                raise HTTPException(status_code=404, detail="Document not found")
            doc = Document(
                id=document_id,
                user=request.user,
                name=request.name,
                content=request.content,
                created=existing.created,
            )
            saved = document_repository.save(doc)
            return DocumentResponse(
                id=saved.id,  # type: ignore[arg-type]
                user=saved.user,
                name=saved.name,
                content=saved.content,
                created=saved.created,
            )

        @app.delete("/documents/{document_id}", status_code=204)
        async def delete_document(document_id: int) -> None:
            deleted = document_repository.delete(document_id)
            if not deleted:
                raise HTTPException(status_code=404, detail="Document not found")

        # htmx endpoints - return HTML fragments
        @app.post("/editor/new", response_class=HTMLResponse)
        async def editor_new() -> str:
            return render_editor(status="New document")

        @app.post("/editor/clear", response_class=HTMLResponse)
        async def editor_clear() -> str:
            return render_editor(status="Cleared")

        @app.post("/editor/save", response_class=HTMLResponse)
        async def editor_save(
            documentId: Annotated[str, Form()] = "",
            documentName: Annotated[str, Form()] = "Untitled document",
            content: Annotated[str, Form()] = "",
            user: Annotated[str, Form()] = "romilly",
        ) -> str:
            # If documentId is set, update existing document
            if documentId:
                doc_id = int(documentId)
                existing = document_repository.load(doc_id)
                if existing:
                    doc = Document(
                        id=doc_id,
                        user=user,
                        name=documentName,
                        content=content,
                        created=existing.created,
                    )
                    saved = document_repository.save(doc)
                    return render_editor(
                        saved.id, saved.name, saved.content, saved.user,
                        status=f'Saved "{saved.name}"',
                    )

            # Otherwise create new document
            doc = Document(
                user=user,
                name=documentName,
                content=content,
                created=datetime.now(),
            )
            saved = document_repository.save(doc)
            return render_editor(
                saved.id, saved.name, saved.content, saved.user,
                status=f'Saved "{saved.name}"',
            )

        @app.get("/editor/load/{document_id}", response_class=HTMLResponse)
        async def editor_load(document_id: int) -> str:
            doc = document_repository.load(document_id)
            if doc is None:
                raise HTTPException(status_code=404, detail="Document not found")
            return render_editor(
                doc.id, doc.name, doc.content, doc.user,
                status=f'Opened "{doc.name}"',
            )

    return app
