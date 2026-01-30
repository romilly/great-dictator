from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Document:
    user: str
    name: str
    content: str
    created: datetime
    id: int | None = None


@dataclass(frozen=True)
class DocumentSummary:
    id: int
    name: str
    created: datetime


class DocumentRepositoryPort(ABC):
    @abstractmethod
    def save(self, document: Document) -> Document:
        pass

    @abstractmethod
    def load(self, document_id: int) -> Document | None:
        pass

    @abstractmethod
    def list_for_user(self, user: str) -> list[DocumentSummary]:
        pass

    @abstractmethod
    def delete(self, document_id: int) -> bool:
        pass
