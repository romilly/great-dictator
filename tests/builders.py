"""Test data builders for the test suite."""

from datetime import datetime

from great_dictator.domain.document import Document

DEFAULT_USER = "romilly"
DEFAULT_CREATED = datetime(2024, 1, 15, 10, 30)


class DocumentBuilder:
    """Fluent builder for Document objects."""

    def __init__(self) -> None:
        self._user = DEFAULT_USER
        self._name = "test doc"
        self._content = "test content"
        self._created = DEFAULT_CREATED
        self._id: int | None = None

    def with_name(self, name: str) -> "DocumentBuilder":
        self._name = name
        return self

    def with_content(self, content: str) -> "DocumentBuilder":
        self._content = content
        return self

    def with_user(self, user: str) -> "DocumentBuilder":
        self._user = user
        return self

    def with_id(self, id: int) -> "DocumentBuilder":
        self._id = id
        return self

    def build(self) -> Document:
        return Document(
            user=self._user,
            name=self._name,
            content=self._content,
            created=self._created,
            id=self._id,
        )


def a_document() -> DocumentBuilder:
    """Factory to start building a Document."""
    return DocumentBuilder()
