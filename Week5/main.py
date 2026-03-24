from fastapi import FastAPI, Query, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, Column, String, Integer, Date, ForeignKey, Table, text
from sqlalchemy.orm import DeclarativeBase, relationship, Session, sessionmaker
from pydantic import BaseModel
from typing import Optional
from datetime import date
import uuid

# ───────────────────────────── Database setup ─────────────────────────────
DATABASE_URL = "sqlite:///./library.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


# ──────────────────────────── Association tables ───────────────────────────
book_author = Table(
    "book_author", Base.metadata,
    Column("book_id",   String, ForeignKey("books.id")),
    Column("author_id", String, ForeignKey("authors.id")),
)

book_category = Table(
    "book_category", Base.metadata,
    Column("book_id",      String, ForeignKey("books.id")),
    Column("category_id",  String, ForeignKey("categories.id")),
)

# ──────────────────────────────── Models ──────────────────────────────────


class Book(Base):
    __tablename__ = "books"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    isbn = Column(String, unique=True)
    published_year = Column(Integer)
    authors = relationship(
        "Author",   secondary=book_author,   back_populates="books")
    categories = relationship(
        "Category", secondary=book_category, back_populates="books")
    copies = relationship("BookCopy", back_populates="book")


class Author(Base):
    __tablename__ = "authors"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    books = relationship("Book", secondary=book_author,
                         back_populates="authors")


class Category(Base):
    __tablename__ = "categories"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    books = relationship("Book", secondary=book_category,
                         back_populates="books")


class BookCopy(Base):
    __tablename__ = "book_copies"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    book_id = Column(String, ForeignKey("books.id"), nullable=False)
    status = Column(String, default="available")   # available | loaned
    book = relationship("Book",  back_populates="copies")
    loans = relationship("Loan",  back_populates="book_copy")


class Member(Base):
    __tablename__ = "members"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    membership_date = Column(Date, default=date.today)
    loans = relationship("Loan", back_populates="member")


class Loan(Base):
    __tablename__ = "loans"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    book_copy_id = Column(String, ForeignKey("book_copies.id"), nullable=False)
    member_id = Column(String, ForeignKey("members.id"),     nullable=False)
    borrowed_at = Column(Date, default=date.today)
    due_date = Column(Date, nullable=False)
    returned_at = Column(Date, nullable=True)
    book_copy = relationship("BookCopy", back_populates="loans")
    member = relationship("Member",   back_populates="loans")


Base.metadata.create_all(engine)

# ─────────────────────────── Pydantic schemas ─────────────────────────────


class BookOut(BaseModel):
    id: str
    title: str
    isbn: Optional[str]
    published_year: Optional[int]
    authors: list[str]
    categories: list[str]
    available_copies: int


# ─────────────────────────────── App ──────────────────────────────────────
app = FastAPI(title="Library Management API", version="1.0")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def book_to_out(book: Book) -> BookOut:
    available = sum(1 for c in book.copies if c.status == "available")
    return BookOut(
        id=book.id,
        title=book.title,
        isbn=book.isbn,
        published_year=book.published_year,
        authors=[a.name for a in book.authors],
        categories=[c.name for c in book.categories],
        available_copies=available,
    )

# ──────────────────────── Seed demo data ──────────────────────────────────


def seed(db: Session):
    if db.query(Book).count() > 0:
        return  # already seeded

    # Authors
    authors = {
        "Clean Code":    Author(id=str(uuid.uuid4()), name="Robert C. Martin"),
        "Design Pat.":   Author(id=str(uuid.uuid4()), name="Gang of Four"),
        "Pragmatic":     Author(id=str(uuid.uuid4()), name="David Thomas"),
        "Python Tricks": Author(id=str(uuid.uuid4()), name="Dan Bader"),
        "Flask Web":     Author(id=str(uuid.uuid4()), name="Miguel Grinberg"),
    }
    db.add_all(authors.values())

    # Categories
    cats = {
        "Programming": Category(id=str(uuid.uuid4()), name="Programming"),
        "Design":      Category(id=str(uuid.uuid4()), name="Software Design"),
        "Python":      Category(id=str(uuid.uuid4()), name="Python"),
        "Web":         Category(id=str(uuid.uuid4()), name="Web Development"),
    }
    db.add_all(cats.values())

    # Books + copies
    books_data = [
        ("Clean Code",                       "978-0132350884",
         2008, ["Clean Code"],    ["Programming", "Design"]),
        ("Design Patterns",                  "978-0201633610",
         1994, ["Design Pat."],   ["Design"]),
        ("The Pragmatic Programmer",         "978-0135957059",
         1999, ["Pragmatic"],     ["Programming"]),
        ("Python Tricks",                    "978-1775093305",
         2017, ["Python Tricks"], ["Python"]),
        ("Flask Web Development",            "978-1491991732",
         2018, ["Flask Web"],     ["Python", "Web"]),
        ("Refactoring",                      "978-0201485677",
         1999, ["Clean Code"],    ["Programming", "Design"]),
        ("Fluent Python",                    "978-1491946008",
         2015, ["Python Tricks"], ["Python"]),
        ("Two Scoops of Django",             "978-0692915729",
         2019, ["Flask Web"],     ["Python", "Web"]),
        ("Head First Design Patterns",       "978-0596007126",
         2004, ["Design Pat."],   ["Design"]),
        ("The Clean Coder",                  "978-0137081073",
         2011, ["Clean Code"],    ["Programming"]),
    ]

    for title, isbn, year, author_keys, cat_keys in books_data:
        book = Book(
            id=str(uuid.uuid4()),
            title=title,
            isbn=isbn,
            published_year=year,
            authors=[authors[k] for k in author_keys],
            categories=[cats[k] for k in cat_keys],
        )
        db.add(book)
        # 2 copies per book
        for _ in range(2):
            db.add(BookCopy(id=str(uuid.uuid4()),
                   book_id=book.id, status="available"))

    db.commit()


with SessionLocal() as _s:
    seed(_s)

# ═══════════════════════════════════════════════════════════════════════════
#  ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

# ── 1. Search + Pagination (offset/limit) ─────────────────────────────────


@app.get("/books", summary="Search sách với offset/limit pagination")
def search_books(
    q:         Optional[str] = Query(
        None,  description="Tìm theo tên sách hoặc tác giả"),
    category:  Optional[str] = Query(None,  description="Lọc theo thể loại"),
    available: Optional[bool] = Query(
        None,  description="Chỉ hiện sách còn bản mượn"),
    offset:    int = Query(0,     ge=0,   description="Bỏ qua N bản ghi đầu"),
    limit:     int = Query(10,    ge=1, le=100,
                           description="Số bản ghi trả về"),
    db: Session = Depends(get_db),
):
    """
    ## Offset / Limit Pagination

    - Đơn giản, dễ hiểu, cho phép nhảy đến bất kỳ trang nào.
    - Nhược điểm: chậm khi offset lớn vì DB phải đọc và bỏ N bản ghi.

    **Ví dụ:** `GET /books?q=python&offset=0&limit=5`
    """
    query = db.query(Book)

    if q:
        query = query.filter(
            Book.title.ilike(f"%{q}%") |
            Book.authors.any(Author.name.ilike(f"%{q}%"))
        )
    if category:
        query = query.filter(Book.categories.any(
            Category.name.ilike(f"%{category}%")))

    total = query.count()
    books = query.offset(offset).limit(limit).all()

    if available is True:
        books = [b for b in books if any(
            c.status == "available" for c in b.copies)]

    return {
        "pagination": {
            "type":     "offset_limit",
            "total":    total,
            "offset":   offset,
            "limit":    limit,
            "has_next": (offset + limit) < total,
            "has_prev": offset > 0,
        },
        "data": [book_to_out(b) for b in books],
    }


# ── 2. Cursor-based Pagination ─────────────────────────────────────────────
@app.get("/books/cursor", summary="Search sách với cursor pagination")
def search_books_cursor(
    q:      Optional[str] = Query(None, description="Tìm theo tên sách"),
    cursor: Optional[str] = Query(None, description="ID cuối của trang trước"),
    limit:  int = Query(5,    ge=1, le=50),
    db: Session = Depends(get_db),
):
    """
    ## Cursor Pagination

    - Hiệu quả hơn offset với dataset lớn (không scan toàn bảng).
    - Không thể nhảy trang, chỉ đi tiếp/lui.
    - Dùng `cursor` = id của phần tử cuối cùng đã nhận.

    **Ví dụ:** `GET /books/cursor?limit=3` → lấy trang đầu  
    **Trang tiếp:** `GET /books/cursor?cursor=<id_cuoi>&limit=3`
    """
    query = db.query(Book).order_by(Book.id)

    if q:
        query = query.filter(Book.title.ilike(f"%{q}%"))

    if cursor:
        query = query.filter(Book.id > cursor)

    books = query.limit(limit + 1).all()

    has_next = len(books) > limit
    books = books[:limit]
    next_cursor = books[-1].id if has_next else None

    return {
        "pagination": {
            "type":        "cursor",
            "limit":       limit,
            "has_next":    has_next,
            "next_cursor": next_cursor,
        },
        "data": [book_to_out(b) for b in books],
    }


# ── 3. Page-based Pagination ───────────────────────────────────────────────
@app.get("/books/page", summary="Search sách với page-based pagination")
def search_books_page(
    q:    Optional[str] = Query(None),
    page: int = Query(1,  ge=1),
    size: int = Query(5,  ge=1, le=50),
    db: Session = Depends(get_db),
):
    """
    ## Page-based Pagination

    - Quen thuộc nhất với người dùng ("Trang 1/10").
    - Thực chất là offset = (page-1) * size, nhược điểm tương tự offset.

    **Ví dụ:** `GET /books/page?page=2&size=3`
    """
    query = db.query(Book)
    if q:
        query = query.filter(Book.title.ilike(f"%{q}%"))

    total = query.count()
    total_pages = (total + size - 1) // size
    offset = (page - 1) * size
    books = query.offset(offset).limit(size).all()

    return {
        "pagination": {
            "type":        "page_based",
            "total":       total,
            "total_pages": total_pages,
            "page":        page,
            "size":        size,
            "has_next":    page < total_pages,
            "has_prev":    page > 1,
        },
        "data": [book_to_out(b) for b in books],
    }


# ── 4. Resource tree: mượn sách ────────────────────────────────────────────
@app.get("/members/{member_id}/loans", summary="Lịch sử mượn sách của thành viên")
def get_member_loans(
    member_id: str,
    returned:  Optional[bool] = Query(
        None, description="True=đã trả, False=đang mượn"),
    db: Session = Depends(get_db),
):
    """Resource tree demo: `/members/{id}/loans`"""
    member = db.get(Member, member_id)
    if not member:
        raise HTTPException(404, "Member not found")

    loans = member.loans
    if returned is True:
        loans = [l for l in loans if l.returned_at is not None]
    elif returned is False:
        loans = [l for l in loans if l.returned_at is None]

    return {
        "member": {"id": member.id, "name": member.full_name},
        "loans": [
            {
                "loan_id":     l.id,
                "book_title":  l.book_copy.book.title,
                "borrowed_at": str(l.borrowed_at),
                "due_date":    str(l.due_date),
                "returned_at": str(l.returned_at) if l.returned_at else None,
            }
            for l in loans
        ],
    }


# ── 5. Health check ───────────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
def root():
    return {"message": "Library API is running. Docs at /docs"}

# pip install -r requirements.txt
# uvicorn main:app --reload
# Mở trình duyệt: http://localhost:8000/docs
