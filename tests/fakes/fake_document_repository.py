from dataclasses import replace

from great_dictator.domain.document import (
    Document,
    DocumentRepositoryPort,
    DocumentSummary,
)


class FakeDocumentRepository(DocumentRepositoryPort):
    def __init__(self) -> None:
        self._documents: dict[int, Document] = {}
        self._next_id = 1

    def save(self, document: Document) -> Document:
        if document.id is not None:
            # Update existing document
            self._documents[document.id] = document
            return document
        else:
            # Create new document
            new_id = self._next_id
            self._next_id += 1
            saved = replace(document, id=new_id)
            self._documents[new_id] = saved
            return saved

    def load(self, document_id: int) -> Document | None:
        return self._documents.get(document_id)

    def list_for_user(self, user: str) -> list[DocumentSummary]:
        return [
            DocumentSummary(id=doc.id, name=doc.name, created=doc.created)  # type: ignore[arg-type]
            for doc in self._documents.values()
            if doc.user == user
        ]

    def delete(self, document_id: int) -> bool:
        if document_id in self._documents:
            del self._documents[document_id]
            return True
        return False
