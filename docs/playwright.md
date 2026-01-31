# Playwright E2E Testing Patterns

Patterns for writing clean, maintainable Playwright E2E tests.

## Core Principle

Extract repeated actions into helper functions in `conftest.py`. This:
- Reduces duplication
- Makes tests more readable
- Expresses intent rather than mechanics

## Fixtures

### `loaded_page` - Page with app loaded

Instead of every test doing:
```python
def test_something(server, server_url, page: Page):
    page.goto(server_url)
    # ... test code
```

Create a fixture:
```python
@pytest.fixture
def loaded_page(server, server_url, page):
    """Page with the app already loaded."""
    page.goto(server_url)
    return page
```

Then tests become:
```python
def test_something(loaded_page: Page):
    # ... test code (page already loaded)
```

## Helper Functions

### `check_visible` - Assert multiple elements visible

Instead of:
```python
expect(page.locator("#elem1")).to_be_visible()
expect(page.locator("#elem2")).to_be_visible()
expect(page.locator("#elem3")).to_be_visible()
```

Create:
```python
def check_visible(page, *selectors: str) -> None:
    """Assert that all given selectors are visible on the page."""
    from playwright.sync_api import expect
    for selector in selectors:
        expect(page.locator(selector)).to_be_visible()
```

Usage:
```python
check_visible(loaded_page, "#elem1", "#elem2", "#elem3")
```

### `wait_for_*` - Wait for async state changes

Extract repeated `wait_for_function` calls:

```python
def wait_for_mic(page) -> None:
    """Wait for microphone selector to be populated."""
    page.wait_for_function(
        "document.getElementById('micSelect').options.length > 0 && "
        "document.getElementById('micSelect').options[0].value !== ''",
        timeout=5000
    )

def wait_for_document_saved(page) -> None:
    """Wait for document to be saved (documentId becomes non-empty)."""
    page.wait_for_function(
        "document.getElementById('documentId').value !== ''",
        timeout=10000
    )

def wait_for_document_cleared(page) -> None:
    """Wait for document to be cleared (documentId becomes empty)."""
    page.wait_for_function(
        "document.getElementById('documentId').value === ''",
        timeout=5000
    )
```

### `click_menu_item` - Multi-step UI actions

Extract repeated click sequences:

```python
def click_menu_item(page, item: str) -> None:
    """Open File menu and click an item."""
    page.click("#fileMenuBtn")
    page.click(f"button:has-text('{item}')")
```

Usage:
```python
click_menu_item(loaded_page, "Save")
wait_for_document_saved(loaded_page)
```

## When to Extract

Extract a helper when:
- The same code appears in **2+ tests**
- The code is **more than 2-3 lines**
- A name would **clarify intent** (e.g., `wait_for_document_saved` vs raw JS)

Don't extract:
- One-off actions
- Simple single-line operations
- When extraction would obscure what's being tested

## File Organisation

```
tests/e2e/
├── conftest.py          # Fixtures and helpers
├── test_*.py            # Test files import from conftest
```

Import helpers explicitly:
```python
from tests.e2e.conftest import check_visible, wait_for_mic, click_menu_item
```
