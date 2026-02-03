"""E2E tests for document operations (save, clear, open, export) with htmx."""
from playwright.sync_api import Page, expect

from tests.e2e.conftest import (
    click_menu_item,
    wait_for_document_cleared,
    wait_for_document_saved,
    wait_for_mic,
)


def test_export_downloads_file_with_content(loaded_page: Page) -> None:
    """Export should download a .txt file with the document content."""
    loaded_page.locator("#docName").fill("My Notes")
    loaded_page.locator("#transcription").fill("Hello world content")

    with loaded_page.expect_download() as download_info:
        click_menu_item(loaded_page, "Export")

    download = download_info.value
    assert download.suggested_filename == "My Notes.txt"

    # Read the downloaded content
    content = download.path().read_text()
    assert content == "Hello world content"


def test_clear_resets_document_state(loaded_page: Page) -> None:
    """After saving a document, Clear should reset to 'Untitled document'.

    With htmx, the server manages state - Clear returns a fresh editor
    with empty document ID and default name.
    """
    loaded_page.locator("#docName").fill("My First Doc")
    loaded_page.locator("#transcription").fill("First document content")

    click_menu_item(loaded_page, "Save")
    wait_for_document_saved(loaded_page)

    expect(loaded_page.locator("#docName")).to_have_value("My First Doc")

    click_menu_item(loaded_page, "Clear")
    wait_for_document_cleared(loaded_page)

    expect(loaded_page.locator("#docName")).to_have_value("Untitled document")
    expect(loaded_page.locator("#transcription")).to_have_value("")


def test_save_then_clear_then_save_creates_new_document(loaded_page: Page) -> None:
    """After Clear, Save should create a new document, not overwrite the old one."""
    loaded_page.locator("#docName").fill("First Doc")
    loaded_page.locator("#transcription").fill("First content")
    click_menu_item(loaded_page, "Save")
    wait_for_document_saved(loaded_page)
    first_doc_id = loaded_page.locator("#documentId").input_value()

    click_menu_item(loaded_page, "Clear")
    wait_for_document_cleared(loaded_page)

    loaded_page.locator("#docName").fill("Second Doc")
    loaded_page.locator("#transcription").fill("Second content")
    click_menu_item(loaded_page, "Save")
    wait_for_document_saved(loaded_page)
    second_doc_id = loaded_page.locator("#documentId").input_value()

    assert first_doc_id != second_doc_id, "Clear then Save should create a new document"


def test_transcription_preserves_document_name(loaded_page: Page) -> None:
    """Document name should be preserved after transcription replaces editor content."""
    wait_for_mic(loaded_page)

    # Set a custom document name
    loaded_page.locator("#docName").fill("My Meeting Notes")

    # Start recording
    loaded_page.click("#record")
    expect(loaded_page.locator("#status")).to_contain_text("Recording", timeout=5000)

    # Record for a moment then stop
    loaded_page.wait_for_timeout(1000)
    loaded_page.click("#stop")

    # Wait for transcription to appear (status changes to "Transcribed")
    expect(loaded_page.locator("#status")).to_contain_text("Transcribed", timeout=30000)

    # Document name should still be "My Meeting Notes", not reset to "Untitled document"
    expect(loaded_page.locator("#docName")).to_have_value("My Meeting Notes")
