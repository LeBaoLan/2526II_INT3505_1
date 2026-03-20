from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

# Khởi tạo thông tin API giống phần "info" trong YAML
app = FastAPI(
    title="API Quản lý sách.",
    description="Hệ thống quản lý thư viện đơn giản chức năng cơ bản.",
    version="1.0.0"
)

# Định nghĩa Schema Book giống hệt phần "components"


class Book(BaseModel):
    id: Optional[int] = None
    title: str
    author: str

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Dế Mèn Phiêu Lưu Ký",
                "author": "Tô Hoài"
            }
        }


# Giả lập Database bằng một List trong RAM
fake_db = []
current_id = 1


@app.get("/books", response_model=List[Book], tags=["Books"], summary="Lấy danh sách tất cả các sách")
def get_books():
    return fake_db


@app.post("/books", response_model=Book, status_code=201, tags=["Books"], summary="Thêm một cuốn sách mới")
def create_book(book: Book):
    global current_id
    book.id = current_id
    fake_db.append(book)
    current_id += 1
    return book


@app.get("/books/{id}", response_model=Book, tags=["Books"], summary="Lấy chi tiết một cuốn sách")
def get_book(id: int):
    for book in fake_db:
        if book.id == id:
            return book
    raise HTTPException(status_code=404, detail="Không tìm thấy sách")


@app.put("/books/{id}", response_model=Book, tags=["Books"], summary="Cập nhật thông tin sách")
def update_book(id: int, updated_book: Book):
    for index, book in enumerate(fake_db):
        if book.id == id:
            updated_book.id = id
            fake_db[index] = updated_book
            return updated_book
    raise HTTPException(
        status_code=404, detail="Không tìm thấy sách để cập nhật")


@app.delete("/books/{id}", status_code=204, tags=["Books"], summary="Xóa một cuốn sách")
def delete_book(id: int):
    for index, book in enumerate(fake_db):
        if book.id == id:
            del fake_db[index]
            return
    raise HTTPException(status_code=404, detail="Không tìm thấy sách để xóa")
