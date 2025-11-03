# tests/test_api.py
import os
import json
from pathlib import Path
import tempfile
from fastapi.testclient import TestClient

# Tạo temp data file trước khi import app
tmpdir = tempfile.TemporaryDirectory()
tmp_path = Path(tmpdir.name)
data_file = tmp_path / "books_with_country.json"
sample_books = [
    {
        "title": "Sample Book A",
        "price": "£10.00",
        "availability": "In stock",
        "product_page_link": "http://example.com/a",
        "star_rating": 4,
        "publisher_country": "Vietnam"
    }
]
data_file.write_text(json.dumps(sample_books, ensure_ascii=False), encoding="utf-8")

os.environ["DATA_FILE"] = str(data_file)
# optional: do not set API_KEY for tests, or set it and include in headers
from api.main import app

client = TestClient(app)

def test_get_books():
    resp = client.get("/books")
    assert resp.status_code == 200
    arr = resp.json()
    assert isinstance(arr, list)
    assert any(b["title"] == "Sample Book A" for b in arr)

def test_filter_by_country():
    resp = client.get("/books?country=Vietnam")
    assert resp.status_code == 200
    arr = resp.json()
    assert len(arr) == 1
    assert arr[0]["publisher_country"] == "Vietnam"

def test_post_and_delete_book():
    new_book = {
        "title": "New Book",
        "price": "£5.00",
        "availability": "In stock",
        "product_page_link": "http://example.com/new",
        "star_rating": 3,
        "publisher_country": "Japan"
    }
    resp = client.post("/books", json=new_book)
    assert resp.status_code == 200
    assert resp.json()["title"] == "New Book"

    # delete
    resp2 = client.delete(f"/books/{new_book['title']}")
    assert resp2.status_code == 204
