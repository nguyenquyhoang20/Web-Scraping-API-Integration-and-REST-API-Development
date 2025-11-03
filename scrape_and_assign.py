import requests
from bs4 import BeautifulSoup
import json
import os
import time
import random
from urllib.parse import urljoin
from pathlib import Path

BASE = "https://books.toscrape.com/"
CATEGORY_RELATIVE = "catalogue/category/books/travel_2/index.html"  # có thể đổi sang "science_22", "poetry_23", ...
PAGES_TO_SCRAPE = 3
DATA_DIR = Path("data")
HTML_BACKUP = Path("html_backup")
CACHE_FILE = DATA_DIR / "countries_cache.json"

DATA_DIR.mkdir(exist_ok=True)
HTML_BACKUP.mkdir(exist_ok=True)

STAR_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (compatible; book-scraper/1.0; +https://example.com)"
})

# ----------------------------- #
#        COUNTRY FETCHING       #
# ----------------------------- #
def get_countries(ttl_hours=24):
    """Lấy danh sách quốc gia từ restcountries.com, có cache và fallback."""
    if CACHE_FILE.exists():
        try:
            payload = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
            fetched = payload.get("_fetched_at", 0)
            if time.time() - fetched < ttl_hours * 3600 and "countries" in payload:
                print("[INFO] Using cached countries list.")
                return payload["countries"]
        except Exception:
            pass

    urls = [
        "https://restcountries.com/v3.1/all",
        "https://restcountries.com/v2/all",  # fallback nếu v3.1 lỗi
    ]

    for url in urls:
        try:
            print(f"[INFO] Fetching from {url} ...")
            r = session.get(url, timeout=15)
            r.raise_for_status()
            arr = r.json()

            countries = []
            for c in arr:
                if isinstance(c, dict):
                    # v3.1 dùng name.common, v2 dùng name
                    name = c.get("name", {}).get("common") if "common" in c.get("name", {}) else c.get("name")
                    if name:
                        countries.append(name)

            if countries:
                CACHE_FILE.write_text(
                    json.dumps({"_fetched_at": time.time(), "countries": countries}, ensure_ascii=False, indent=2),
                    encoding="utf-8"
                )
                print(f"[INFO] Saved {len(countries)} countries to cache.")
                return countries
        except Exception as e:
            print(f"[WARN] Failed fetching from {url}: {e}")

    print("[ERROR] Could not fetch countries from any endpoint.")
    return ["Unknown"]

# ----------------------------- #
#        SCRAPER FUNCTIONS      #
# ----------------------------- #
def parse_book_article(article, page_url):
    title = article.h3.a["title"].strip()
    href = article.h3.a["href"]
    product_link = urljoin(page_url, href)
    price = article.select_one(".price_color").text.strip()
    availability = article.select_one(".availability").text.strip()
    classes = article.select_one("p.star-rating")["class"]
    star_word = next((c for c in classes if c != "star-rating"), None)
    star = STAR_MAP.get(star_word, 0)
    return {
        "title": title,
        "price": price,
        "availability": availability,
        "product_page_link": product_link,
        "star_rating": star,
    }

def save_html(url, filename):
    try:
        r = session.get(url, timeout=10)
        r.raise_for_status()
        HTML_BACKUP.joinpath(filename).write_bytes(r.content)
    except Exception as e:
        print(f"[WARN] save_html failed for {url}: {e}")

def scrape_category(category_relative, pages=3):
    books = []
    next_url = urljoin(BASE, category_relative)
    for i in range(pages):
        print(f"[INFO] Scraping page {i+1}: {next_url}")
        r = session.get(next_url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        articles = soup.select("article.product_pod")

        for art in articles:
            book = parse_book_article(art, next_url)
            books.append(book)

            safe_title = "".join(c for c in book["title"] if c.isalnum() or c in (" ", "-", "_")).rstrip()
            filename = f"{safe_title[:60].replace(' ', '_')}.html"
            save_html(book["product_page_link"], filename)

        next_btn = soup.select_one("li.next > a")
        if next_btn:
            next_href = next_btn["href"]
            next_url = urljoin(next_url, next_href)
            time.sleep(1)
        else:
            break
    return books

def assign_random_countries(books, countries):
    for b in books:
        b["publisher_country"] = random.choice(countries) if countries else "Unknown"
    return books

# ----------------------------- #
#             MAIN              #
# ----------------------------- #
def main():
    print("[INFO] Fetching countries (with cache)...")
    countries = get_countries()
    print(f"[INFO] Got {len(countries)} countries.")

    books = scrape_category(CATEGORY_RELATIVE, pages=PAGES_TO_SCRAPE)
    DATA_DIR.joinpath("books.json").write_text(
        json.dumps(books, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    books_with = assign_random_countries(books, countries)
    DATA_DIR.joinpath("books_with_country.json").write_text(
        json.dumps(books_with, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print("[INFO] Saved data to data/books.json and data/books_with_country.json")

if __name__ == "__main__":
    main()
