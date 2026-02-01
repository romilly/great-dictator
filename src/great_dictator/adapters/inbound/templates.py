"""HTML template rendering using Jinja2."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

from jinja2 import Environment, FileSystemLoader, select_autoescape

# Set up Jinja2 environment with auto-escaping for security
TEMPLATES_DIR = Path(__file__).parent / "templates"
_env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(["html", "xml"]),
)


def render_editor(
    document_id: Optional[int] = None,
    document_name: str = "Untitled document",
    content: str = "",
    user: str = "romilly",
    status: str = "",
) -> str:
    """Render the editor HTML fragment."""
    template = _env.get_template("editor.html")
    return template.render(
        document_id=document_id if document_id else "",
        document_name=document_name,
        content=content,
        user=user,
        status=status,
    )


def render_document_list(documents: List[Tuple[int, str, datetime]]) -> str:
    """Render the document list HTML fragment."""
    template = _env.get_template("document_list.html")
    return template.render(documents=documents)
