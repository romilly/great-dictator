from playwright.sync_api import Page, expect


def test_page_loads(server, server_url, page: Page):
    """Test that the page loads with correct elements."""
    page.goto(server_url)

    # Verify page loaded
    expect(page.locator("h1")).to_have_text("Great Dictator")

    # Verify mic selector exists
    expect(page.locator("#micSelect")).to_be_visible()

    # Verify buttons exist
    expect(page.locator("#record")).to_be_visible()
    expect(page.locator("#stop")).to_be_visible()

    # Verify textarea exists
    expect(page.locator("#transcription")).to_be_visible()


def test_microphone_populates(server, server_url, page: Page):
    """Test that the microphone selector populates with devices."""
    page.goto(server_url)

    # Wait for microphone to be populated
    page.wait_for_function(
        "document.getElementById('micSelect').options.length > 0 && "
        "document.getElementById('micSelect').options[0].value !== ''",
        timeout=5000
    )

    # Should have at least one option with a value
    mic_select = page.locator("#micSelect")
    expect(mic_select).to_be_visible()


def test_file_menu_opens(server, server_url, page: Page):
    """Test that the File menu opens and shows expected options."""
    page.goto(server_url)

    # Verify File menu button exists
    file_menu_btn = page.locator("#fileMenuBtn")
    expect(file_menu_btn).to_have_text("File")

    # Dropdown should be hidden initially
    dropdown = page.locator("#fileDropdown")
    expect(dropdown).not_to_be_visible()

    # Click File menu
    file_menu_btn.click()

    # Dropdown should now be visible with options
    expect(dropdown).to_be_visible()
    expect(dropdown.locator("button:has-text('New')")).to_be_visible()
    expect(dropdown.locator("button:has-text('Open')")).to_be_visible()
    expect(dropdown.locator("button:has-text('Save')")).to_be_visible()
    expect(dropdown.locator("button:has-text('Copy')")).to_be_visible()
    expect(dropdown.locator("button:has-text('Clear')")).to_be_visible()

    # Click outside to close
    page.click("h1")
    expect(dropdown).not_to_be_visible()


def test_recording_starts(server, server_url, page: Page):
    """Test that clicking Record starts recording."""
    page.goto(server_url)

    # Wait for microphone to be populated
    page.wait_for_function(
        "document.getElementById('micSelect').options.length > 0 && "
        "document.getElementById('micSelect').options[0].value !== ''",
        timeout=5000
    )

    # Click Record
    page.click("#record")

    # Wait for recording status
    expect(page.locator("#status")).to_contain_text("Recording", timeout=5000)

    # Record should be disabled, Stop should be enabled
    expect(page.locator("#record")).to_be_disabled()
    expect(page.locator("#stop")).to_be_enabled()

    # Click Stop
    page.click("#stop")

    # Record should be enabled again
    expect(page.locator("#record")).to_be_enabled()
