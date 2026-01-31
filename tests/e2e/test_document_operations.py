"""E2E tests for document operations (save, clear, open) with htmx."""
from playwright.sync_api import Page, expect


def test_clear_resets_document_state(loaded_page: Page) -> None:
    """After saving a document, Clear should reset to 'Untitled document'.

    With htmx, the server manages state - Clear returns a fresh editor
    with empty document ID and default name.
    """
    # Set document name and content
    loaded_page.locator("#docName").fill("My First Doc")
    loaded_page.locator("#transcription").fill("First document content")

    # Save the document
    loaded_page.locator("#fileMenuBtn").click()
    loaded_page.locator("button:has-text('Save')").click()

    # Wait for htmx to complete - the hidden documentId should be set
    loaded_page.wait_for_function(
        "document.getElementById('documentId').value !== ''",
        timeout=10000
    )

    # Verify document name is still there
    expect(loaded_page.locator("#docName")).to_have_value("My First Doc")

    # Now click Clear
    loaded_page.locator("#fileMenuBtn").click()
    loaded_page.locator("button:has-text('Clear')").click()

    # Wait for htmx to complete - documentId should be empty again
    loaded_page.wait_for_function(
        "document.getElementById('documentId').value === ''",
        timeout=5000
    )

    # Document name should reset to "Untitled document"
    expect(loaded_page.locator("#docName")).to_have_value("Untitled document")

    # Textarea should be empty
    expect(loaded_page.locator("#transcription")).to_have_value("")


def test_save_then_clear_then_save_creates_new_document(loaded_page: Page) -> None:
    """After Clear, Save should create a new document, not overwrite the old one."""
    # Save first document
    loaded_page.locator("#docName").fill("First Doc")
    loaded_page.locator("#transcription").fill("First content")
    loaded_page.locator("#fileMenuBtn").click()
    loaded_page.locator("button:has-text('Save')").click()

    # Wait for save to complete
    loaded_page.wait_for_function(
        "document.getElementById('documentId').value !== ''",
        timeout=5000
    )
    first_doc_id = loaded_page.locator("#documentId").input_value()

    # Clear
    loaded_page.locator("#fileMenuBtn").click()
    loaded_page.locator("button:has-text('Clear')").click()

    # Wait for clear to complete
    loaded_page.wait_for_function(
        "document.getElementById('documentId').value === ''",
        timeout=5000
    )

    # Save second document with different name
    loaded_page.locator("#docName").fill("Second Doc")
    loaded_page.locator("#transcription").fill("Second content")
    loaded_page.locator("#fileMenuBtn").click()
    loaded_page.locator("button:has-text('Save')").click()

    # Wait for save to complete
    loaded_page.wait_for_function(
        "document.getElementById('documentId').value !== ''",
        timeout=5000
    )
    second_doc_id = loaded_page.locator("#documentId").input_value()

    # The two document IDs should be different
    assert first_doc_id != second_doc_id, "Clear then Save should create a new document"
