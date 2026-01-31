from playwright.sync_api import Page, expect

from tests.e2e.conftest import check_visible, wait_for_mic


def test_page_loads(loaded_page: Page):
    """Test that the page loads with correct elements."""
    expect(loaded_page.locator("h1")).to_have_text("Great Dictator")
    check_visible(loaded_page, "#micSelect", "#record", "#stop", "#transcription")


def test_microphone_populates(loaded_page: Page):
    """Test that the microphone selector populates with devices."""
    wait_for_mic(loaded_page)
    check_visible(loaded_page, "#micSelect")


def test_file_menu_opens(loaded_page: Page):
    """Test that the File menu opens and shows expected options."""
    expect(loaded_page.locator("#fileMenuBtn")).to_have_text("File")
    expect(loaded_page.locator("#fileDropdown")).not_to_be_visible()

    # Click File menu
    loaded_page.click("#fileMenuBtn")

    # Dropdown should now be visible with menu items
    check_visible(
        loaded_page,
        "#fileDropdown",
        "button:has-text('New')",
        "button:has-text('Open')",
        "button:has-text('Save')",
        "button:has-text('Export')",
        "button:has-text('Copy')",
        "button:has-text('Clear')",
    )

    # Click outside to close
    loaded_page.click("h1")
    expect(loaded_page.locator("#fileDropdown")).not_to_be_visible()


def test_recording_starts(loaded_page: Page):
    """Test that clicking Record starts recording."""
    wait_for_mic(loaded_page)
    loaded_page.click("#record")

    # Wait for recording status
    expect(loaded_page.locator("#status")).to_contain_text("Recording", timeout=5000)

    # Record should be disabled, Stop should be enabled
    expect(loaded_page.locator("#record")).to_be_disabled()
    expect(loaded_page.locator("#stop")).to_be_enabled()

    # Click Stop
    loaded_page.click("#stop")

    # Record should be enabled again
    expect(loaded_page.locator("#record")).to_be_enabled()
