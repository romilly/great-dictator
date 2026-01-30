# Progress Report: Document Storage & Database Configuration

**Date:** 2026-01-30

## Summary

Added persistent document storage with SQLite and refactored database configuration to use environment variables via .env files.

## What Was Built

### Domain Layer (`src/great_dictator/domain/document.py`)
- `Document` dataclass (id, user, name, content, created)
- `DocumentSummary` dataclass for list views (id, name, created)
- `DocumentRepositoryPort` abstract base class defining CRUD operations:
  - `save(document)` - create or update
  - `load(document_id)` - retrieve by ID
  - `list_for_user(user)` - list user's documents
  - `delete(document_id)` - remove document

### Outbound Adapter (`src/great_dictator/adapters/outbound/sqlite_document_repository.py`)
- `SqliteDocumentRepository` implementing DocumentRepositoryPort
- Uses `CREATE TABLE IF NOT EXISTS` to preserve data
- Unique constraint on (user, name) to prevent duplicates
- Auto-incrementing ID assignment on insert

### Database Configuration
- **`.env`** (project root): `DATABASE_PATH=data/documents.db`
- **`tests/.env`**: `DATABASE_PATH=tests/data/test_documents.db`
- `app.py` loads database path from environment using python-dotenv
- Separate databases for testing and production

### Test Infrastructure (`tests/conftest.py`)
- New `db_repository` fixture for integration tests
- Uses persistent test database at `tests/data/test_documents.db`
- Cleans data with DELETE (not DROP) to preserve schema
- Data persists after tests for debugging

## Tests Implemented

### Integration Tests (`tests/integration/test_sqlite_repository.py`)
- `test_save_assigns_id_to_new_document`
- `test_load_returns_none_for_missing_document`
- `test_load_returns_saved_document`
- `test_save_updates_existing_document`
- `test_list_for_user_returns_only_users_documents`
- `test_delete_removes_document`
- `test_delete_returns_false_for_missing_document`
- `test_unique_constraint_on_user_and_name`

### Smoke Test (`tests/integration/test_production_db.py`)
- `test_production_db_connects` - verifies production database connectivity

## Dependencies Added

**requirements.txt:**
- python-dotenv

## Files Modified/Created

### New Files
- `src/great_dictator/domain/document.py`
- `src/great_dictator/adapters/outbound/sqlite_document_repository.py`
- `tests/integration/test_sqlite_repository.py`
- `tests/integration/test_production_db.py`
- `.env`
- `tests/.env`

### Modified Files
- `src/great_dictator/app.py` - loads DB path from environment
- `tests/conftest.py` - added db_repository fixture
- `.gitignore` - added `*.db` pattern
- `requirements.txt` - added python-dotenv

## Test Results

All tests passing:
- 8 sqlite repository integration tests
- 1 production db smoke test

Type checking: 0 errors (pyright)

## Architecture Notes

The document storage follows hexagonal architecture:
- Domain defines the port (DocumentRepositoryPort)
- SQLite adapter implements the port
- Composition root wires the adapter into the application

Database path is externalized to environment variables, allowing:
- Different databases for test vs production
- Easy configuration changes without code modifications
- Test data inspection after test runs

## htmx Refactoring (Later Same Day)

### What Was Done

Refactored the frontend from JavaScript to htmx for server-side state management.

### Frontend Changes (`src/great_dictator/static/index.html`)
- Added htmx from CDN
- Document name changed from JavaScript `prompt()` to editable input field
- File menu operations (New, Clear, Save) now use htmx attributes (`hx-post`, `hx-target`, `hx-swap`)
- Open dialog loads document list via htmx
- Transcription uses `htmx.ajax()` for server requests

### JavaScript Retained (Can't Be Replaced by htmx)
- Menu dropdown toggle
- Clipboard copy (browser API)
- Modal open/close
- MediaRecorder audio capture (Web API)

### New htmx Endpoints (`src/great_dictator/adapters/inbound/fastapi_app.py`)
- `POST /editor/new` - returns empty editor fragment
- `POST /editor/clear` - returns cleared editor fragment
- `POST /editor/save` - saves document, returns editor with updated ID
- `GET /editor/load/{id}` - loads document into editor
- `GET /documents/list-html` - returns document list as HTML
- `POST /transcribe` - now returns htmx fragment when `HX-Request` header present

### Jinja2 Templates (`src/great_dictator/adapters/inbound/templates/`)
- `editor.html` - editor fragment with document ID, name, content, status
- `document_list.html` - clickable list of user's documents
- `templates.py` - rendering functions with auto-escaping for XSS protection

### Test Infrastructure
- `tests/e2e/conftest.py` - database cleanup between E2E tests
- `tests/unit/test_templates.py` - template rendering tests including XSS protection
- Updated E2E tests for new htmx-based UI

### Dependencies Added
- jinja2 (for template rendering)

### Bug Fixed
- Clear now properly resets document state (server manages state, not browser)

## Test Results (Final)

All 40 tests passing:
- 4 E2E tests
- 11 integration tests (API, document API, sqlite, whisper, production db)
- 9 unit tests (document, templates, transcription)

Type checking: 0 errors (pyright)

## Next Steps

- User authentication integration
- Multiple user support in UI

---

## TODO: Create /web Skill

**Reminder:** Create a `/web` skill/command that specifies the standard web stack:
- **FastAPI** for backend
- **htmx** for frontend interactivity
- **Jinja2** for server-side templates
- **Server-side state management** (not client-side JavaScript)
