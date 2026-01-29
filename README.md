# great-dictator

A browser-based dictation engine for workstation or phone.

## Features

- Browser-based audio recording using MediaRecorder API
- Speech-to-text transcription using faster-whisper
- Simple web interface with Record/Stop controls
- File menu for managing transcriptions (Copy, Save, Save As)
- Hexagonal architecture for clean separation of concerns

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Inbound Adapter                        │
│                   (FastAPI + HTML/JS)                       │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Domain Layer                             │
│         TranscriptionService ←── TranscriberPort (ABC)      │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                     Outbound Adapter                        │
│                   (WhisperTranscriber)                      │
└─────────────────────────────────────────────────────────────┘
```

## Installation

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -e .
```

## Running the Application

```bash
source venv/bin/activate
./scripts/dev-server.sh
```

Or manually:
```bash
uvicorn great_dictator.app:app --reload --port 8765
```

Then open http://localhost:8765 in your browser.

**Note:** Dev server uses port 8765, E2E tests use port 8766 to avoid conflicts.

## Development

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Install Playwright browsers
playwright install chromium

# Run all tests
pytest

# Run specific test suites
pytest tests/unit/           # Unit tests
pytest tests/integration/    # Integration tests
pytest tests/e2e/            # End-to-end tests

# Type checking
pyright src/
```

## Project Structure

```
src/great_dictator/
├── app.py                          # Composition root
├── domain/
│   └── transcription.py            # Domain layer (ports & services)
├── adapters/
│   ├── inbound/
│   │   └── fastapi_app.py          # FastAPI routes
│   └── outbound/
│       └── whisper_transcriber.py  # Whisper implementation
└── static/
    └── index.html                  # Web UI

tests/
├── unit/                           # Domain layer tests
├── integration/                    # Adapter tests
└── e2e/
    ├── conftest.py                 # Server fixtures (port 8766)
    └── test_dictation_flow.py      # Playwright browser tests

scripts/
└── dev-server.sh                   # Dev server launcher (port 8765)
```

## License

MIT
