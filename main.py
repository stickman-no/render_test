import os
from typing import Optional, List
import uvicorn
from fastapi import FastAPI, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="Books CRUD Service",
    description="A premium FastAPI service designed for managing a books library, complete with full CRUD capability.",
    version="1.1.0"
)

# Enable CORS for convenience
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

# In-memory database with pre-populated premium books
books_db: dict[int, dict] = {
    1: {
        "id": 1,
        "title": "To Kill a Mockingbird",
        "author": "Harper Lee",
        "published_year": 1960,
        "genre": "Fiction",
        "description": "The memorable novel of a childhood in a sleepy Southern town and the crisis of conscience that rocked it."
    },
    2: {
        "id": 2,
        "title": "1984",
        "author": "George Orwell",
        "published_year": 1949,
        "genre": "Dystopian",
        "description": "A classic dystopian novel about totalitarianism, surveillance, and individual freedom."
    },
    3: {
        "id": 3,
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "published_year": 1925,
        "genre": "Fiction",
        "description": "A portrait of the Jazz Age in all its decadence and excess, focusing on the mysterious Jay Gatsby."
    }
}

# Keep a counter to generate unique IDs
id_counter = 3

@app.get("/")
def read_root():
    return {
        "message": "Hello",
        "docs_url": "/docs",
        "description": "Welcome to the Books CRUD API. Visit /docs for the interactive Swagger UI."
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# --- CRUD Endpoints ---

# 1. Create a Book
@app.post("/books", response_model=Book, status_code=status.HTTP_201_CREATED)
def create_book(book_in: BookCreate):
    global id_counter
    id_counter += 1
    new_book = {
        "id": id_counter,
        **book_in.model_dump()
    }
    books_db[id_counter] = new_book
    return new_book

# 2. Get All Books (with optional query filters)
@app.get("/books", response_model=List[Book])
def get_books(
    author: Optional[str] = Query(None, description="Filter books by author (case-insensitive)"),
    genre: Optional[str] = Query(None, description="Filter books by genre (case-insensitive)")
):
    results = list(books_db.values())
    
    if author:
        author_lower = author.lower()
        results = [b for b in results if author_lower in b["author"].lower()]
        
    if genre:
        genre_lower = genre.lower()
        results = [b for b in results if genre_lower in b["genre"].lower()]
        
    return results

# 3. Get a Book by ID
@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int):
    book = books_db.get(book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found."
        )
    return book

# 4. Update a Book
@app.put("/books/{book_id}", response_model=Book)
def update_book(book_id: int, book_in: BookUpdate):
    book = books_db.get(book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found."
        )
    
    # Update fields that were provided
    update_data = book_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        book[key] = value
        
    books_db[book_id] = book
    return book

# 5. Delete a Book
@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int):
    if book_id not in books_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found."
        )
    del books_db[book_id]
    return

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
