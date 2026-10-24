
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Response, status
from pydantic import BaseModel, Field



app = FastAPI(
    title="Book Management API",
    description="A simple REST API for managing books.",
    version="1.0.0",
)


class BookInput(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0)
    publication_year: int = Field(ge=1, le=2100)


class Book(BookInput):
    id: int


books: dict[int, Book] = {}
next_id = 1


@app.get("/")
def home():
    return {
        "message": "Welcome to the Book Management API",
        "docs": "/docs",
    }


@app.get("/books", response_model=list[Book])
def get_books(
    title: Optional[str] = Query(default=None),
    author: Optional[str] = Query(default=None),
):
    results = list(books.values())

    if title:
        results = [
            book for book in results
            if title.casefold() in book.title.casefold()
        ]

    if author:
        results = [
            book for book in results
            if author.casefold() in book.author.casefold()
        ]

    return results


@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int):
    book = books.get(book_id)

    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )

    return book


@app.post(
    "/books",
    response_model=Book,
    status_code=status.HTTP_201_CREATED,
)
def create_book(book_input: BookInput):
    global next_id

    book = Book(id=next_id, **book_input.model_dump())
    books[next_id] = book
    next_id += 1

    return book


@app.put("/books/{book_id}", response_model=Book)
def update_book(book_id: int, book_input: BookInput):
    if book_id not in books:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )

    updated_book = Book(
        id=book_id,
        **book_input.model_dump(),
    )

    books[book_id] = updated_book
    return updated_book


@app.delete(
    "/books/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_book(book_id: int):
    if book_id not in books:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )

    del books[book_id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)
