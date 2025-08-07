from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException
from typing import List
from src.books.schemas import Books, BookUpdate
from src.books.book_data import books

book_router = APIRouter()

@book_router.get("/", response_model= List[Books])
async def get_all_books():
    return books

@book_router.post("/", status_code= status.HTTP_201_CREATED)
async def publish_a_book(book: Books) -> dict:
    new_book = book.model_dump()
    books.book_routerend(new_book)

    return new_book

@book_router.get("/{book_id}")
async def get_a_book(book_id: int) -> dict:
    for book in books:
        if book["id"] == book_id:
            return book
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

@book_router.patch("/{book_id}")
async def update_a_book(book_id: int, update_book: BookUpdate) -> dict:
    for book in books:
        if book["id"] == book_id:
            book['title'] = update_book.title
            book['author'] = update_book.author
            book['publisher'] = update_book.publisher
            book['page_count'] = update_book.page_count
            book['language'] = update_book.language
            return book
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

@book_router.delete("/{book_id}", status_code= status.HTTP_204_NO_CONTENT)
async def delete_a_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            books.remove(book)
            return {}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")