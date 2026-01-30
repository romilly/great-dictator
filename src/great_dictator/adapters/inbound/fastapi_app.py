from datetime import datetime
from io import BytesIO
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel

from great_dictator.domain.document import Document, DocumentRepositoryPort
from great_dictator.domain.transcription import TranscriptionService

STATIC_DIR = Path(__file__).parent.parent.parent / "static"


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
    document_repository: DocumentRepositoryPort | None = None,
) -> FastAPI:
    app = FastAPI()

    @app.get("/", response_class=HTMLResponse)
    async def index() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    @app.post("/transcribe", response_class=HTMLResponse)
    async def transcribe(audio: UploadFile = File(...)) -> str:
        audio_bytes = await audio.read()
        result = transcription_service.transcribe(BytesIO(audio_bytes))
        return result.text

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

    return app
