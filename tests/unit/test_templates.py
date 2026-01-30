"""Unit tests for HTML template rendering."""
from datetime import datetime

from hamcrest import assert_that, contains_string, equal_to

from great_dictator.adapters.inbound.templates import render_editor, render_document_list


def test_render_editor_empty_document() -> None:
    html = render_editor()

    assert_that(html, contains_string('value=""'))  # empty document ID
    assert_that(html, contains_string('value="Untitled document"'))
    assert_that(html, contains_string('name="content"'))


def test_render_editor_with_document() -> None:
    html = render_editor(
        document_id=42,
        document_name="My Doc",
        content="Hello world",
        user="testuser",
    )

    assert_that(html, contains_string('value="42"'))
    assert_that(html, contains_string('value="My Doc"'))
    assert_that(html, contains_string('value="testuser"'))
    assert_that(html, contains_string("Hello world"))


def test_render_editor_escapes_html() -> None:
    html = render_editor(
        document_name="<script>alert('xss')</script>",
        content="<b>bold</b>",
    )

    # Should escape HTML to prevent XSS
    assert_that(html, contains_string("&lt;script&gt;"))
    assert_that(html, contains_string("&lt;b&gt;"))


def test_render_editor_with_status_message() -> None:
    html = render_editor(status="Document saved")

    assert_that(html, contains_string("Document saved"))
    assert_that(html, contains_string('id="status"'))


def test_render_editor_without_status_message() -> None:
    html = render_editor()

    # Status div should still exist but be empty
    assert_that(html, contains_string('id="status"'))


def test_render_document_list_empty() -> None:
    html = render_document_list([])

    assert_that(html, contains_string("No documents found"))


def test_render_document_list_with_documents() -> None:
    documents = [
        (1, "First Doc", datetime(2024, 1, 15, 10, 30)),
        (2, "Second Doc", datetime(2024, 1, 16, 14, 0)),
    ]

    html = render_document_list(documents)

    assert_that(html, contains_string("First Doc"))
    assert_that(html, contains_string("Second Doc"))
    assert_that(html, contains_string('hx-get="/editor/load/1"'))
    assert_that(html, contains_string('hx-get="/editor/load/2"'))
    assert_that(html, contains_string("2024-01-15"))
    assert_that(html, contains_string("2024-01-16"))


def test_render_document_list_escapes_html() -> None:
    documents = [
        (1, "<script>alert('xss')</script>", datetime(2024, 1, 15, 10, 30)),
    ]

    html = render_document_list(documents)

    # Should escape HTML to prevent XSS
    assert_that(html, contains_string("&lt;script&gt;"))
