import subprocess
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError

import pytest
from playwright.sync_api import Page, expect

TEST_AUDIO_PATH = Path(__file__).parent.parent / "data" / "test_audio.wav"


def wait_for_server(url: str, max_attempts: int = 30):
    """Poll until server is ready."""
    for _ in range(max_attempts):
        try:
            urlopen(url, timeout=1)
            return
        except URLError:
            import time
            time.sleep(0.1)
    raise RuntimeError(f"Server at {url} did not start")


@pytest.fixture(scope="session")
def server():
    """Start the FastAPI server for E2E tests."""
    proc = subprocess.Popen(
        ["uvicorn", "great_dictator.app:app", "--port", "8765"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    wait_for_server("http://localhost:8765")
    yield proc
    proc.terminate()
    proc.wait()


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser with fake audio capture."""
    return {
        **browser_context_args,
        "permissions": ["microphone"],
    }


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """Configure Chrome with fake media stream using test audio file."""
    return {
        **browser_type_launch_args,
        "args": [
            "--use-fake-device-for-media-stream",
            "--use-fake-ui-for-media-stream",
            f"--use-file-for-fake-audio-capture={TEST_AUDIO_PATH.absolute()}",
        ],
    }


def test_dictation_flow(server, page: Page):
    """Test the full dictation flow: record -> stop -> see transcription."""
    page.goto("http://localhost:8765")

    # Verify page loaded
    expect(page.locator("h1")).to_have_text("Great Dictator")

    # Wait for microphone to be populated and select it
    page.wait_for_function(
        "document.getElementById('micSelect').options.length > 0 && "
        "document.getElementById('micSelect').options[0].value !== ''",
        timeout=5000
    )

    # Click Record
    page.click("#record")

    # Wait for recording status
    expect(page.locator("#status")).to_have_text("Recording...", timeout=5000)

    # Wait for enough audio to be captured
    page.wait_for_timeout(2000)

    # Click Stop
    page.click("#stop")

    # Wait for transcription to appear (Whisper processing can take time)
    transcription = page.locator("#transcription")

    # Wait until textarea has a value containing "hello"
    page.wait_for_function(
        "document.getElementById('transcription').value.toLowerCase().includes('hello')",
        timeout=60000
    )


def test_file_menu_opens(server, page: Page):
    """Test that the File menu opens and shows expected options."""
    page.goto("http://localhost:8765")

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
    expect(dropdown.locator("#copy")).to_have_text("Copy")
    expect(dropdown.locator("#save")).to_have_text("Save")
    expect(dropdown.locator("#saveAs")).to_have_text("Save As")

    # Click outside to close
    page.click("h1")
    expect(dropdown).not_to_be_visible()
