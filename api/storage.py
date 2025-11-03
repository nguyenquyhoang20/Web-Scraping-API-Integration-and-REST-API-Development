# api/storage.py
from pathlib import Path
import json

def load_books(path: Path):
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []

def save_books(path: Path, books):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(books, ensure_ascii=False, indent=2), encoding="utf-8")
