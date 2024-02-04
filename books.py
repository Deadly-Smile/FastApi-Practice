from typing import Optional
from uuid import UUID
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()


class Book(BaseModel):
    id: UUID
    title: str = Field(min_length=3, max_length=63)
    author: str = Field(min_length=3, max_length=31)
    publisher: str = Field(min_length=3, max_length=63)
    description: Optional[str] = Field(title="A short description of book", min_length=1, max_length=100)
    rating: float = Field(ge=0.00, le=5.00)

    # This thing doesn't work
    class Config:
        schema_extra = {
            "example": {
                "id": "a5335640-41f4-4210-ac3c-79a16fc7a38c",
                "title": "The title of book",
                "author": "The author of this book",
                "publisher": "The publisher of this book",
                "description": "A short description of book",
                "rating": "A number between 0.0 and 5.00"
            }
        }


BOOKS = []


@app.get("/books")
async def get_books():
    return BOOKS


@app.post("/books")
async def create_book(book: Book):
    BOOKS.append(book)
    return book


@app.put("/books/{id}")
async def update_book(id: UUID, book: Book):
    index = 0
    for b in BOOKS:
        if b.id == id:
            BOOKS[index] = book
            break
        index += 1

    return {"message": "Book updated", "book": BOOKS[index]}


@app.delete("/books/{id}")
async def delete_book(id: UUID):
    index = 0
    for b in BOOKS:
        if b.id == id:
            del BOOKS[index]
        index += 1
    return {"message": "Book deleted", "book": id}


@app.get("/books/{id}")
async def get_book(id: UUID):
    for b in BOOKS:
        if b.id == id:
            return {"message": "Book found", "book": b}

    return {"message": "Not found"}
