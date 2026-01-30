from datetime import datetime

import pytest
from hamcrest import assert_that, equal_to, is_

from great_dictator.domain.document import Document, DocumentSummary


def test_document_is_frozen():
    doc = Document(
        user="romilly",
        name="test doc",
        content="hello world",
        created=datetime(2024, 1, 15, 10, 30),
    )

    with pytest.raises(AttributeError):
        doc.content = "changed"  # type: ignore[misc]


def test_document_without_id_is_new():
    doc = Document(
        user="romilly",
        name="test doc",
        content="hello world",
        created=datetime(2024, 1, 15, 10, 30),
    )

    assert_that(doc.id, is_(None))


def test_document_with_id_is_not_new():
    doc = Document(
        user="romilly",
        name="test doc",
        content="hello world",
        created=datetime(2024, 1, 15, 10, 30),
        id=42,
    )

    assert_that(doc.id, equal_to(42))


def test_document_summary_has_required_fields():
    summary = DocumentSummary(
        id=1,
        name="test doc",
        created=datetime(2024, 1, 15, 10, 30),
    )

    assert_that(summary.id, equal_to(1))
    assert_that(summary.name, equal_to("test doc"))
