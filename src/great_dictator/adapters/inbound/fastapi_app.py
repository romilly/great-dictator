from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel

from great_dictator.domain.document import Document, DocumentRepositoryPort
from great_dictator.domain.transcription import TranscriptionService

STATIC_DIR = Path(__file__).parent.parent.parent / "static"


def render_editor(
    document_id: int | None = None,
    document_name: str = "Untitled document",
    content: str = "",
    user: str = "romilly",
) -> str:
    """Render the editor HTML fragment for htmx responses."""
    doc_id_value = str(document_id) if document_id else ""
    return f"""<div id="docTitle">
    <input type="hidden" name="documentId" id="documentId" value="{doc_id_value}">
    <input type="hidden" name="user" value="{user}">
    <input type="text" id="docName" name="documentName" value="{document_name}" placeholder="Document name">
</div>
<textarea id="transcription" name="content" placeholder="Transcription will appear here...">{content}</textarea>"""


def render_document_list(documents: list[tuple[int, str, datetime]]) -> str:
    """Render the document list HTML fragment for htmx responses."""
    if not documents:
        return '<li style="color: #666; cursor: default;">No documents found</li>'

    items = []
    for doc_id, name, created in documents:
        date_str = created.strftime("%Y-%m-%d %H:%M")
        items.append(
            f'''<li hx-get="/editor/load/{doc_id}" hx-target="#editor-area" hx-swap="innerHTML">
    <div class="doc-name">{name}</div>
    <div class="doc-date">{date_str}</div>
</li>'''
        )
    return "\n".join(items)


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

        # htmx endpoints - return HTML fragments
        @app.post("/editor/new", response_class=HTMLResponse)
        async def editor_new() -> str:
            return render_editor()

        @app.post("/editor/clear", response_class=HTMLResponse)
        async def editor_clear() -> str:
            return render_editor()

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
                    return render_editor(saved.id, saved.name, saved.content, saved.user)

            # Otherwise create new document
            doc = Document(
                user=user,
                name=documentName,
                content=content,
                created=datetime.now(),
            )
            saved = document_repository.save(doc)
            return render_editor(saved.id, saved.name, saved.content, saved.user)

        @app.get("/editor/load/{document_id}", response_class=HTMLResponse)
        async def editor_load(document_id: int) -> str:
            doc = document_repository.load(document_id)
            if doc is None:
                raise HTTPException(status_code=404, detail="Document not found")
            return render_editor(doc.id, doc.name, doc.content, doc.user)

        @app.get("/documents/list-html", response_class=HTMLResponse)
        async def documents_list_html(user: str) -> str:
            summaries = document_repository.list_for_user(user)
            documents = [(s.id, s.name, s.created) for s in summaries]
            return render_document_list(documents)

    return app
