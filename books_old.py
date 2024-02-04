from typing import Optional

from fastapi import FastAPI
from enum import Enum

app = FastAPI()

BOOKS = {
    "book_1": {"title": "Book 1", "author": "Author1", "price": 100},
    "book_2": {"title": "Book 2", "author": "Author2", "price": 150},
    "book_3": {"title": "Book 3", "author": "Author3", "price": 250},
    "book_4": {"title": "Book 4", "author": "Author4", "price": 300},
    "book_5": {"title": "Book 5", "author": "Author5", "price": 500},
    "book_6": {"title": "Book 6", "author": "Author6", "price": 900},
    "book_7": {"title": "Book 7", "author": "Author7", "price": 200},
    "book_8": {"title": "Book 8", "author": "Author8", "price": 300}
}


class Direction(str, Enum):
    North: str = "North"
    South: str = "South"
    East: str = "East"
    West: str = "West"


@app.get('/books')
async def get_all_books(skip_book: Optional[str] = None):
    if skip_book:
        sending_books = BOOKS.copy()
        sending_books.pop(skip_book)
        return {"books": sending_books}
    return {"books": BOOKS}


@app.post('/books')
async def create_book(title: str, author: str, price: int):
    book_id = 1
    if len(BOOKS):
        for book in BOOKS:
            book_id = max(book_id, int(book.split("_")[-1]))

    BOOKS[f"book_{book_id}"] = {"title": title, "author": author, "price": price}
    return {"new book": BOOKS[f"book_{book_id}"]}


@app.put('/books/{book_id}')
async def update_book(title: str, author: str, price: int, book_id: int):
    book = BOOKS[f"book_{book_id}"]
    if book:
        book = {"title": title, "author": author, "price": price}
        BOOKS[f"book_{book_id}"] = book
        return {"updated book": book}
    else:
        return {"error": "Book does not exist"}


@app.delete('/books/{book_id}')
async def delete_book(book_id: int):
    del BOOKS[f"book_{book_id}"]
    return {"deleted book": f"book_{book_id}"}


@app.get('/books/{book_key}')
async def get_book(book_key: str):
    return {"book": BOOKS[book_key]}


@app.get("/direction/{direction}")
async def get_direction(direction: Direction):
    if direction == Direction.North:
        return {'direction': Direction.North, 'symbol': 'Up'}
    elif direction == Direction.South:
        return {'direction': Direction.South, 'symbol': 'Down'}
    elif direction == Direction.West:
        return {'direction': Direction.West, 'symbol': 'Left'}
    else:
        return {'direction': Direction.East, 'symbol': 'Right'}
