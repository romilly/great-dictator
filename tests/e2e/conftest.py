"""E2E test fixtures with proper server management."""
import subprocess
import time
from contextlib import contextmanager
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

import pytest

# Test server uses different port from manual testing (8765)
TEST_SERVER_PORT = 8766
TEST_SERVER_URL = f"http://localhost:{TEST_SERVER_PORT}"
TEST_AUDIO_PATH = Path(__file__).parent.parent / "data" / "test_audio.wav"


def wait_for_server(url: str, max_attempts: int = 30):
    """Poll until server is ready."""
    for _ in range(max_attempts):
        try:
            urlopen(url, timeout=1)
            return
        except URLError:
            time.sleep(0.1)
    raise RuntimeError(f"Server at {url} did not start")


@contextmanager
def managed_server(port: int):
    """Context manager that ensures clean server shutdown.

    - Waits up to 5 seconds for graceful termination
    - Force kills if still running
    """
    proc = subprocess.Popen(
        ["uvicorn", "great_dictator.app:app", "--port", str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        wait_for_server(f"http://localhost:{port}")
        yield proc
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()


@pytest.fixture(scope="session")
def server():
    """Start the FastAPI server for E2E tests on port 8766."""
    with managed_server(TEST_SERVER_PORT) as proc:
        yield proc


@pytest.fixture(scope="session")
def server_url():
    """URL for the test server."""
    return TEST_SERVER_URL


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
