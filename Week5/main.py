from pydantic import BaseModel
from fastapi import FastAPI, Query, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy import create_engine, Column, String, Integer, Date, ForeignKey, Table, asc, desc
from sqlalchemy.orm import DeclarativeBase, relationship, Session, sessionmaker
from typing import Optional, Literal
from datetime import date
import uuid

engine = create_engine("sqlite:///./library.db",
                       connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


book_author = Table("book_author", Base.metadata,
                    Column("book_id",   String, ForeignKey("books.id")),
                    Column("author_id", String, ForeignKey("authors.id")))

book_category = Table("book_category", Base.metadata,
                      Column("book_id",     String, ForeignKey("books.id")),
                      Column("category_id", String, ForeignKey("categories.id")))


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
                         back_populates="categories")


class BookCopy(Base):
    __tablename__ = "book_copies"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    book_id = Column(String, ForeignKey("books.id"), nullable=False)
    status = Column(String, default="available")
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

# --- Response helpers ---


def ok(data, meta=None):
    body = {"success": True, "data": data}
    if meta:
        body["meta"] = meta
    return JSONResponse(content=body)


def err(code: int, message: str, detail=None):
    body = {"success": False, "error": {"code": code, "message": message}}
    if detail:
        body["error"]["detail"] = detail
    return JSONResponse(status_code=code, content=body)


# --- App + error handlers ---
app = FastAPI(title="Library API", version="2.0")


@app.exception_handler(RequestValidationError)
async def on_validation_error(request: Request, exc: RequestValidationError):
    errors = [{"field": ".".join(
        str(l) for l in e["loc"]), "msg": e["msg"]} for e in exc.errors()]
    return err(422, "Invalid parameters", errors)


@app.exception_handler(HTTPException)
async def on_http_error(request: Request, exc: HTTPException):
    return err(exc.status_code, exc.detail)

# --- DB + helpers ---


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


SORT = {"title": Book.title, "published_year": Book.published_year, "id": Book.id}


def apply_sort(q, sort_by, order):
    return q.order_by(asc(SORT.get(sort_by, Book.title)) if order == "asc" else desc(SORT.get(sort_by, Book.title)))


def book_out(b: Book) -> dict:
    return {
        "id": b.id, "title": b.title, "isbn": b.isbn,
        "published_year": b.published_year,
        "authors": [a.name for a in b.authors],
        "categories": [c.name for c in b.categories],
        "available_copies": sum(1 for c in b.copies if c.status == "available"),
    }


def loan_out(l: Loan) -> dict:
    return {
        "loan_id": l.id, "book_title": l.book_copy.book.title,
        "borrowed_at": str(l.borrowed_at), "due_date": str(l.due_date),
        "returned_at": str(l.returned_at) if l.returned_at else None,
        "is_overdue": l.returned_at is None and l.due_date < date.today(),
    }

# --- Seed ---


def seed(db: Session):
    if db.query(Book).count() > 0:
        return
    authors = {
        "RC Martin": Author(id=str(uuid.uuid4()), name="Robert C. Martin"),
        "GoF":       Author(id=str(uuid.uuid4()), name="Gang of Four"),
        "D Thomas":  Author(id=str(uuid.uuid4()), name="David Thomas"),
        "D Bader":   Author(id=str(uuid.uuid4()), name="Dan Bader"),
        "M Grinberg": Author(id=str(uuid.uuid4()), name="Miguel Grinberg"),
    }
    cats = {
        "Prog":   Category(id=str(uuid.uuid4()), name="Programming"),
        "Design": Category(id=str(uuid.uuid4()), name="Software Design"),
        "Python": Category(id=str(uuid.uuid4()), name="Python"),
        "Web":    Category(id=str(uuid.uuid4()), name="Web Development"),
    }
    db.add_all(list(authors.values()) + list(cats.values()))
    for title, isbn, year, ak, ck in [
        ("Clean Code",                 "978-0132350884",
         2008, ["RC Martin"],   ["Prog", "Design"]),
        ("Design Patterns",            "978-0201633610",
         1994, ["GoF"],         ["Design"]),
        ("The Pragmatic Programmer",   "978-0135957059",
         1999, ["D Thomas"],    ["Prog"]),
        ("Python Tricks",              "978-1775093305",
         2017, ["D Bader"],     ["Python"]),
        ("Flask Web Development",      "978-1491991732",
         2018, ["M Grinberg"],  ["Python", "Web"]),
        ("Refactoring",                "978-0201485677",
         1999, ["RC Martin"],   ["Prog", "Design"]),
        ("Fluent Python",              "978-1491946008",
         2015, ["D Bader"],     ["Python"]),
        ("Two Scoops of Django",       "978-0692915729",
         2019, ["M Grinberg"],  ["Python", "Web"]),
        ("Head First Design Patterns", "978-0596007126",
         2004, ["GoF"],         ["Design"]),
        ("The Clean Coder",            "978-0137081073",
         2011, ["RC Martin"],   ["Prog"]),
    ]:
        b = Book(id=str(uuid.uuid4()), title=title, isbn=isbn, published_year=year,
                 authors=[authors[k] for k in ak], categories=[cats[k] for k in ck])
        db.add(b)
        db.add_all([BookCopy(id=str(uuid.uuid4()), book_id=b.id)
                   for _ in range(2)])
    db.commit()


with SessionLocal() as _s:
    seed(_s)

# =============================================================================
# ENDPOINTS
# =============================================================================


@app.get("/books")
def search_books(
    q:         Optional[str] = Query(None, min_length=1, max_length=100),
    author:    Optional[str] = Query(None, min_length=1, max_length=100),
    category:  Optional[str] = Query(None, min_length=1, max_length=50),
    year_from: Optional[int] = Query(None, ge=1000, le=2100),
    year_to:   Optional[int] = Query(None, ge=1000, le=2100),
    available: Optional[bool] = Query(None),
    sort_by:   Literal["title", "published_year", "id"] = Query("title"),
    order:     Literal["asc", "desc"] = Query("asc"),
    offset:    int = Query(0,  ge=0),
    limit:     int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    if year_from and year_to and year_from > year_to:
        raise HTTPException(400, "year_from must be <= year_to")
    q_ = db.query(Book)
    if q:
        q_ = q_.filter(Book.title.ilike(f"%{q}%") | Book.authors.any(
            Author.name.ilike(f"%{q}%")))
    if author:
        q_ = q_.filter(Book.authors.any(Author.name.ilike(f"%{author}%")))
    if category:
        q_ = q_.filter(Book.categories.any(
            Category.name.ilike(f"%{category}%")))
    if year_from:
        q_ = q_.filter(Book.published_year >= year_from)
    if year_to:
        q_ = q_.filter(Book.published_year <= year_to)
    q_ = apply_sort(q_, sort_by, order)
    total = q_.count()
    books = q_.offset(offset).limit(limit).all()
    if available is True:
        books = [b for b in books if any(
            c.status == "available" for c in b.copies)]
    return ok([book_out(b) for b in books], {"pagination": {
        "type": "offset_limit", "total": total, "offset": offset, "limit": limit,
        "has_next": (offset + limit) < total, "has_prev": offset > 0,
    }, "sort": {"sort_by": sort_by, "order": order}})


@app.get("/books/cursor")
def search_books_cursor(
    q:        Optional[str] = Query(None, min_length=1, max_length=100),
    author:   Optional[str] = Query(None, min_length=1, max_length=100),
    category: Optional[str] = Query(None, min_length=1, max_length=50),
    sort_by:  Literal["title", "id"] = Query("id"),
    order:    Literal["asc", "desc"] = Query("asc"),
    cursor:   Optional[str] = Query(None),
    limit:    int = Query(5, ge=1, le=50),
    db: Session = Depends(get_db),
):
    col = SORT.get(sort_by, Book.id)
    q_ = db.query(Book)
    if q:
        q_ = q_.filter(Book.title.ilike(f"%{q}%") | Book.authors.any(
            Author.name.ilike(f"%{q}%")))
    if author:
        q_ = q_.filter(Book.authors.any(Author.name.ilike(f"%{author}%")))
    if category:
        q_ = q_.filter(Book.categories.any(
            Category.name.ilike(f"%{category}%")))
    q_ = q_.order_by(asc(col) if order == "asc" else desc(col))
    if cursor:
        q_ = q_.filter(col > cursor) if order == "asc" else q_.filter(
            col < cursor)
    books = q_.limit(limit + 1).all()
    has_next = len(books) > limit
    books = books[:limit]
    return ok([book_out(b) for b in books], {"pagination": {
        "type": "cursor", "limit": limit, "has_next": has_next,
        "next_cursor": getattr(books[-1], sort_by) if has_next and books else None,
        "current_cursor": cursor,
    }, "sort": {"sort_by": sort_by, "order": order}})


@app.get("/books/page")
def search_books_page(
    q:         Optional[str] = Query(None, min_length=1, max_length=100),
    author:    Optional[str] = Query(None, min_length=1, max_length=100),
    category:  Optional[str] = Query(None, min_length=1, max_length=50),
    year_from: Optional[int] = Query(None, ge=1000, le=2100),
    year_to:   Optional[int] = Query(None, ge=1000, le=2100),
    sort_by:   Literal["title", "published_year", "id"] = Query("title"),
    order:     Literal["asc", "desc"] = Query("asc"),
    page:      int = Query(1, ge=1),
    size:      int = Query(5, ge=1, le=50),
    db: Session = Depends(get_db),
):
    if year_from and year_to and year_from > year_to:
        raise HTTPException(400, "year_from must be <= year_to")
    q_ = db.query(Book)
    if q:
        q_ = q_.filter(Book.title.ilike(f"%{q}%") | Book.authors.any(
            Author.name.ilike(f"%{q}%")))
    if author:
        q_ = q_.filter(Book.authors.any(Author.name.ilike(f"%{author}%")))
    if category:
        q_ = q_.filter(Book.categories.any(
            Category.name.ilike(f"%{category}%")))
    if year_from:
        q_ = q_.filter(Book.published_year >= year_from)
    if year_to:
        q_ = q_.filter(Book.published_year <= year_to)
    q_ = apply_sort(q_, sort_by, order)
    total = q_.count()
    total_pages = max((total + size - 1) // size, 1)
    if page > total_pages:
        raise HTTPException(
            400, f"page={page} exceeds total_pages={total_pages}")
    books = q_.offset((page - 1) * size).limit(size).all()
    return ok([book_out(b) for b in books], {"pagination": {
        "type": "page_based", "total": total, "total_pages": total_pages,
        "page": page, "size": size,
        "has_next": page < total_pages, "has_prev": page > 1,
    }, "sort": {"sort_by": sort_by, "order": order}})


@app.get("/members/{member_id}/loans")
def get_member_loans(
    member_id: str,
    returned:  Optional[bool] = Query(None),
    overdue:   Optional[bool] = Query(None),
    sort_by:   Literal["borrowed_at", "due_date"] = Query("borrowed_at"),
    order:     Literal["asc", "desc"] = Query("desc"),
    db: Session = Depends(get_db),
):
    member = db.get(Member, member_id)
    if not member:
        raise HTTPException(404, f"Member '{member_id}' not found")
    loans = member.loans
    if returned is True:
        loans = [l for l in loans if l.returned_at is not None]
    if returned is False:
        loans = [l for l in loans if l.returned_at is None]
    if overdue is True:
        loans = [
            l for l in loans if l.returned_at is None and l.due_date < date.today()]
    loans = sorted(loans, key=lambda l: getattr(l, sort_by)
                   or date.min, reverse=(order == "desc"))
    return ok({
        "member":  {"id": member.id, "name": member.full_name, "email": member.email},
        "loans":   [loan_out(l) for l in loans],
        "summary": {
            "total":    len(member.loans),
            "active":   sum(1 for l in member.loans if l.returned_at is None),
            "returned": sum(1 for l in member.loans if l.returned_at is not None),
            "overdue":  sum(1 for l in member.loans if l.returned_at is None and l.due_date < date.today()),
        }
    })


@app.get("/books/{book_id}")
def get_book(book_id: str, db: Session = Depends(get_db)):
    book = db.get(Book, book_id)
    if not book:
        raise HTTPException(404, f"Book '{book_id}' not found")
    return ok(book_out(book))


# --- Pydantic schemas cho write operations ---


class BookIn(BaseModel):
    title:          str
    isbn:           Optional[str] = None
    published_year: Optional[int] = None
    author_names:   list[str] = []
    category_names: list[str] = []


def get_or_create_authors(names: list[str], db: Session) -> list[Author]:
    result = []
    for name in names:
        author = db.query(Author).filter(Author.name == name).first()
        if not author:
            author = Author(id=str(uuid.uuid4()), name=name)
            db.add(author)
        result.append(author)
    return result


def get_or_create_categories(names: list[str], db: Session) -> list[Category]:
    result = []
    for name in names:
        cat = db.query(Category).filter(Category.name == name).first()
        if not cat:
            cat = Category(id=str(uuid.uuid4()), name=name)
            db.add(cat)
        result.append(cat)
    return result


@app.post("/books", status_code=201)
def create_book(body: BookIn, db: Session = Depends(get_db)):
    if body.isbn and db.query(Book).filter(Book.isbn == body.isbn).first():
        raise HTTPException(409, f"ISBN '{body.isbn}' already exists")
    book = Book(
        id=str(uuid.uuid4()), title=body.title,
        isbn=body.isbn, published_year=body.published_year,
        authors=get_or_create_authors(body.author_names, db),
        categories=get_or_create_categories(body.category_names, db),
    )
    db.add(book)
    db.add_all([BookCopy(id=str(uuid.uuid4()), book_id=book.id)
               for _ in range(2)])
    db.commit()
    db.refresh(book)
    return ok(book_out(book), status_code=201)


@app.put("/books/{book_id}")
def update_book(book_id: str, body: BookIn, db: Session = Depends(get_db)):
    book = db.get(Book, book_id)
    if not book:
        raise HTTPException(404, f"Book '{book_id}' not found")
    if body.isbn and body.isbn != book.isbn:
        if db.query(Book).filter(Book.isbn == body.isbn).first():
            raise HTTPException(409, f"ISBN '{body.isbn}' already exists")
    book.title = body.title
    book.isbn = body.isbn
    book.published_year = body.published_year
    book.authors = get_or_create_authors(body.author_names, db)
    book.categories = get_or_create_categories(body.category_names, db)
    db.commit()
    db.refresh(book)
    return ok(book_out(book))


@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: str, db: Session = Depends(get_db)):
    book = db.get(Book, book_id)
    if not book:
        raise HTTPException(404, f"Book '{book_id}' not found")
    active_loans = [
        c for c in book.copies for l in c.loans if l.returned_at is None]
    if active_loans:
        raise HTTPException(409, "Cannot delete book with active loans")
    db.delete(book)
    db.commit()
    from fastapi.responses import Response
    return Response(status_code=204)


@app.get("/", include_in_schema=False)
def root(): return ok({"message": "Library API v2", "docs": "/docs"})
