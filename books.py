import json
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel, Field
from custom_response import ThrowException, Response

app = FastAPI()


class Book:
    id: int
    title: str
    author: str
    publisher: str
    description: Optional[str]
    rating: float

    current_count = 0

    def __init__(self, title: str, author: str, publisher: str, description: Optional[str] = None,
                 rating: Optional[float] = 3.5):
        Book.current_count += 1
        self.id = Book.current_count
        self.title = title
        self.author = author
        self.publisher = publisher
        self.description = description
        self.rating = rating

    def update(self, title: str, author: str, publisher: str, description: Optional[str] = None,
               rating: Optional[float] = 3.5):
        self.title = title
        self.author = author
        self.publisher = publisher
        self.description = description
        self.rating = rating


class BookRequest(BaseModel):
    id: Optional[int] = None
    title: str = Field(min_length=3, max_length=63)
    author: str = Field(min_length=3, max_length=31)
    publisher: str = Field(min_length=3, max_length=63)
    description: Optional[str] = Field(title="A short description of book", min_length=1, max_length=100)
    rating: float = Field(ge=0.00, le=5.00)

    class Config:
        json_schema_extra = {
            'example': {
                'title': 'A new book',
                'author': 'Anik Saha',
                'description': 'A new description of a book',
                'rating': 5,
                'publisher': "Some publisher"
            }
        }


BOOKS = []


@app.get("/books")
async def get_books():
    if len(BOOKS) == 0:
        create_dummy_book_object()
    return BOOKS


@app.post("/books")
async def create_book(book: BookRequest):
    BOOKS.append(Book(book.title, book.author, book.publisher, book.description, book.rating))
    return book


@app.put("/books/{id}")
async def update_book(book_id: int, book: BookRequest):
    index = 0
    for b in BOOKS:
        if b.id == book_id:
            BOOKS[index].update(title=book.title, author=book.author, publisher=book.publisher,
                                description=book.description, rating=book.rating)

            return {"message": "Book updated", "book": BOOKS[index]}
            # return Response(content={"message": "Book updated", "book": BOOKS[index]}, status_code=200,
            #                 headers="book is updated")
        index += 1
    raise ThrowException(404, "Book not found")


@app.delete("/books/{id}")
async def delete_book(book_id: int):
    index = 0
    for b in BOOKS:
        if b.id == book_id:
            del BOOKS[index]
            return {"message": "Book deleted", "book": book_id}
        index += 1
    raise ThrowException(404, "Book does not", "Book does not exist")


@app.get("/books/{id}")
async def get_book(book_id: int):
    for b in BOOKS:
        if b.id == book_id:
            return {"message": "Book found", "book": b}

    raise ThrowException(404, "Book does not", "Book does not")


def create_dummy_book_object():
    BOOKS.append(Book(title="Book 1", author="author 1", publisher="publisher 1", description="a short description",
                      rating=4.2))
    BOOKS.append(Book(title="Book 2", author="author 2", publisher="publisher 2", description="a short description",
                      rating=4.1))
    BOOKS.append(Book(title="Book 3", author="author 3", publisher="publisher 3", description="a short description",
                      rating=3.6))
    BOOKS.append(Book(title="Book 4", author="author 4", publisher="publisher 4", description="a short description",
                      rating=4.8))
