# api/main.py
import os
import json
from fastapi import FastAPI, HTTPException, Query, Header, Depends
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
from .storage import load_books, save_books
from .logger import logger

DATA_FILE = Path(os.getenv("DATA_FILE", "data/books_with_country.json"))
API_KEY = os.getenv("API_KEY")  # optional: if set, require X-API-KEY header

app = FastAPI(title="Books API", version="1.0.0")

books = []  # in-memory copy


class Book(BaseModel):
    title: str
    price: str
    availability: str
    product_page_link: str
    star_rating: int
    publisher_country: str


def check_api_key(x_api_key: Optional[str] = Header(None)):
    if API_KEY:
        if not x_api_key or x_api_key != API_KEY:
            raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return True


@app.on_event("startup")
def startup_event():
    global books
    logger.info(f"Loading books from {DATA_FILE}")
    books = load_books(DATA_FILE)
    logger.info(f"Loaded {len(books)} books")


@app.get("/books", response_model=List[Book], dependencies=[Depends(check_api_key)])
def get_books(country: Optional[str] = Query(None, description="Filter by publisher country")):
    if country:
        filtered = [b for b in books if b.get("publisher_country", "").lower() == country.lower()]
        return filtered
    return books


@app.post("/books", response_model=Book, dependencies=[Depends(check_api_key)])
def add_book(book: Book):
    global books
    if any(b["title"].lower() == book.title.lower() for b in books):
        raise HTTPException(status_code=400, detail="Book with this title already exists")
    books.append(book.dict())
    save_books(DATA_FILE, books)
    logger.info(f"Added book: {book.title}")
    return book


@app.delete("/books/{title}", status_code=204, dependencies=[Depends(check_api_key)])
def delete_book(title: str):
    global books
    before = len(books)
    books = [b for b in books if b["title"].lower() != title.lower()]
    if len(books) == before:
        raise HTTPException(status_code=404, detail="Book not found")
    save_books(DATA_FILE, books)
    logger.info(f"Deleted book: {title}")
    return None
