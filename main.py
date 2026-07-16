import os
from typing import Optional, List
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI, HTTPException, status, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session

# Import DB config
from database import engine, SessionLocal, get_db
import models

# Lifespan for startup DB creation and seeding
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-create tables (SQLite or PostgreSQL)
    models.Base.metadata.create_all(bind=engine)
    
    # Pre-populate database if empty
    db = SessionLocal()
    try:
        if db.query(models.DBBook).count() == 0:
            default_books = [
                models.DBBook(
                    title="To Kill a Mockingbird",
                    author="Harper Lee",
                    published_year=1960,
                    genre="Fiction",
                    description="The memorable novel of a childhood in a sleepy Southern town and the crisis of conscience that rocked it."
                ),
                models.DBBook(
                    title="1984",
                    author="George Orwell",
                    published_year=1949,
                    genre="Dystopian",
                    description="A classic dystopian novel about totalitarianism, surveillance, and individual freedom."
                ),
                models.DBBook(
                    title="The Great Gatsby",
                    author="F. Scott Fitzgerald",
                    published_year=1925,
                    genre="Fiction",
                    description="A portrait of the Jazz Age in all its decadence and excess, focusing on the mysterious Jay Gatsby."
                )
            ]
            db.add_all(default_books)
            db.commit()
    finally:
        db.close()
    yield

app = FastAPI(
    title="Books CRUD Service (Relational)",
    description="A premium FastAPI service designed for managing a books library, powered by SQLite (local) and PostgreSQL (Render).",
    version="1.2.0",
    lifespan=lifespan
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Schemas
class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="The title of the book", examples=["The Hobbit"])
    author: str = Field(..., min_length=1, max_length=100, description="The author of the book", examples=["J.R.R. Tolkien"])
    published_year: Optional[int] = Field(None, ge=0, le=2100, description="The year the book was published", examples=[1937])
    genre: Optional[str] = Field(None, min_length=1, max_length=50, description="The genre of the book", examples=["Fantasy"])
    description: Optional[str] = Field(None, max_length=500, description="A brief description of the book")

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    author: Optional[str] = Field(None, min_length=1, max_length=100)
    published_year: Optional[int] = Field(None, ge=0, le=2100)
    genre: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=500)

class Book(BookBase):
    id: int = Field(..., description="The unique identifier of the book")
    
    model_config = ConfigDict(from_attributes=True)

@app.get("/")
def read_root():
    return {
        "message": "Hello",
        "docs_url": "/docs",
        "database_type": "PostgreSQL" if os.environ.get("DATABASE_URL") else "SQLite (Local)",
        "description": "Welcome to the Books CRUD API. Visit /docs for the interactive Swagger UI."
    }

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        # Quick query to ensure DB connection works
        db.execute(models.Base.metadata.tables["books"].select().limit(1))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database connection failed: {str(e)}"
        )

# --- CRUD Endpoints ---

# 1. Create a Book
@app.post("/books", response_model=Book, status_code=status.HTTP_201_CREATED)
def create_book(book_in: BookCreate, db: Session = Depends(get_db)):
    db_book = models.DBBook(**book_in.model_dump())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

# 2. Get All Books (with optional query filters)
@app.get("/books", response_model=List[Book])
def get_books(
    author: Optional[str] = Query(None, description="Filter books by author (case-insensitive)"),
    genre: Optional[str] = Query(None, description="Filter books by genre (case-insensitive)"),
    db: Session = Depends(get_db)
):
    query = db.query(models.DBBook)
    
    if author:
        query = query.filter(models.DBBook.author.ilike(f"%{author}%"))
        
    if genre:
        query = query.filter(models.DBBook.genre.ilike(f"%{genre}%"))
        
    return query.all()

# 3. Get a Book by ID
@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int, db: Session = Depends(get_db)):
    db_book = db.query(models.DBBook).filter(models.DBBook.id == book_id).first()
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found."
        )
    return db_book

# 4. Update a Book
@app.put("/books/{book_id}", response_model=Book)
def update_book(book_id: int, book_in: BookUpdate, db: Session = Depends(get_db)):
    db_book = db.query(models.DBBook).filter(models.DBBook.id == book_id).first()
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found."
        )
    
    # Update fields that were provided
    update_data = book_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_book, key, value)
        
    db.commit()
    db.refresh(db_book)
    return db_book

# 5. Delete a Book
@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    db_book = db.query(models.DBBook).filter(models.DBBook.id == book_id).first()
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found."
        )
    db.delete(db_book)
    db.commit()
    return

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
