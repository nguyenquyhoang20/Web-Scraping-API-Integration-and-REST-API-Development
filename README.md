
# BOOK SCRAPER API

## Giới thiệu
Bài test này bao gồm 3 phần:
1. **Web Scraping:** Thu thập dữ liệu sách từ website https://books.toscrape.com  
2. **External API Integration:** Gọi API https://restcountries.com để gán quốc gia ngẫu nhiên cho từng sách  
3. **REST API:** Xây dựng API với FastAPI để thao tác với dữ liệu sách  

---

## Phần 1: Web Scraping

### Yêu cầu
- Truy cập trang: https://books.toscrape.com  
- Chọn 1 danh mục (ví dụ: Travel, Science, Poetry, ...)  
- Thu thập dữ liệu ít nhất 3 trang gồm các thông tin:
  - Tiêu đề (Title)
  - Giá (Price)
  - Tình trạng (Availability)
  - Link sản phẩm (Product Page Link)
  - Số sao (Star Rating – đổi ra số 1 đến 5)
- Lưu dữ liệu vào file `data/books.json`
- Lưu HTML từng trang vào thư mục `html_backup/`

## Phần 2: Gọi API bên ngoài

### Yêu cầu
- Dùng API [https://restcountries.com](https://restcountries.com) để lấy danh sách quốc gia.  
- Gán ngẫu nhiên một quốc gia cho mỗi sách scraped ở phần 1.  
- Lưu dữ liệu mới vào `data/books_with_country.json`.

---

## Phần 3: Xây dựng REST API

### Công nghệ
- **FastAPI**
- **Python 3.12**
- **Uvicorn** để chạy server

### Cài đặt thư viện
Chạy lệnh:
```bash
pip install -r requirements.txt

Cách chạy chương trình
Bước 1: Chạy thu thập dữ liệu (Phần 1 + 2)
python scrape_and_assign.py


Sau khi chạy xong sẽ có:

data/books.json

data/books_with_country.json

html_backup/ chứa file HTML

Bước 2: Chạy API (Phần 3)
uvicorn api.main:app --reload


API chạy tại:

http://127.0.0.1:8000


Mở Postman để test:

http://127.0.0.1:8000/docs

Một số endpoint:

GET /books → Lấy tất cả sách

GET /books?country=France → Lọc sách theo quốc gia

POST /books → Thêm sách mới

DELETE /books/{title} → Xóa sách theo tiêu đề

Chạy bằng Docker (tuỳ chọn)
docker-compose up --build
hoặc
docker build -t books-api .
docker run -p 8000:8000 books-api

Tác giả

Họ tên: Nguyễn Quý Hoàng
Năm: 2025

