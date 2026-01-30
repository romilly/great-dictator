import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv


def test_production_db_connects() -> None:
    # Temporarily load root .env
    load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / ".env")
    db_path = os.getenv("DATABASE_PATH")
    assert db_path is not None, "DATABASE_PATH not set in root .env"

    # Ensure the database directory exists
    db_dir = Path(db_path).parent
    db_dir.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.close()
