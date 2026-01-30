"""E2E tests for document operations (save, clear, open) with htmx."""
from playwright.sync_api import Page, expect


def test_clear_resets_document_state(server, server_url, page: Page) -> None:
    """After saving a document, Clear should reset to 'Untitled document'.

    With htmx, the server manages state - Clear returns a fresh editor
    with empty document ID and default name.
    """
    page.goto(server_url)

    # Set document name and content
    page.locator("#docName").fill("My First Doc")
    page.locator("#transcription").fill("First document content")

    # Save the document
    page.locator("#fileMenuBtn").click()
    page.locator("button:has-text('Save')").click()

    # Wait for htmx to complete - the hidden documentId should be set
    page.wait_for_function(
        "document.getElementById('documentId').value !== ''",
        timeout=10000
    )

    # Verify document name is still there
    expect(page.locator("#docName")).to_have_value("My First Doc")

    # Now click Clear
    page.locator("#fileMenuBtn").click()
    page.locator("button:has-text('Clear')").click()

    # Wait for htmx to complete - documentId should be empty again
    page.wait_for_function(
        "document.getElementById('documentId').value === ''",
        timeout=5000
    )

    # Document name should reset to "Untitled document"
    expect(page.locator("#docName")).to_have_value("Untitled document")

    # Textarea should be empty
    expect(page.locator("#transcription")).to_have_value("")


def test_save_then_clear_then_save_creates_new_document(
    server, server_url, page: Page
) -> None:
    """After Clear, Save should create a new document, not overwrite the old one."""
    page.goto(server_url)

    # Save first document
    page.locator("#docName").fill("First Doc")
    page.locator("#transcription").fill("First content")
    page.locator("#fileMenuBtn").click()
    page.locator("button:has-text('Save')").click()

    # Wait for save to complete
    page.wait_for_function(
        "document.getElementById('documentId').value !== ''",
        timeout=5000
    )
    first_doc_id = page.locator("#documentId").input_value()

    # Clear
    page.locator("#fileMenuBtn").click()
    page.locator("button:has-text('Clear')").click()

    # Wait for clear to complete
    page.wait_for_function(
        "document.getElementById('documentId').value === ''",
        timeout=5000
    )

    # Save second document with different name
    page.locator("#docName").fill("Second Doc")
    page.locator("#transcription").fill("Second content")
    page.locator("#fileMenuBtn").click()
    page.locator("button:has-text('Save')").click()

    # Wait for save to complete
    page.wait_for_function(
        "document.getElementById('documentId').value !== ''",
        timeout=5000
    )
    second_doc_id = page.locator("#documentId").input_value()

    # The two document IDs should be different
    assert first_doc_id != second_doc_id, "Clear then Save should create a new document"
