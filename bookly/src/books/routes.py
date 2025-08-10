from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List
from src.books.schemas import Books, BookUpdate, BookCreateModel
# from src.books.models import Book
from src.books.service import BookService
# from src.books.book_data import books
from src.db.main import get_session

book_router = APIRouter()
book_service = BookService()

@book_router.get("/", response_model= List[Books])
async def get_all_books(session: AsyncSession = Depends(get_session)):
    books = await book_service.get_all_books(session)
    return books

@book_router.post("/", status_code= status.HTTP_201_CREATED, response_model=Books)
async def publish_a_book(book: BookCreateModel, session: AsyncSession = Depends(get_session)) -> dict:
    # new_book = book.model_dump()
    new_book = await book_service.create_book(book, session)
    # books.append(new_book)
    return new_book

@book_router.get("/{book_id}", response_model=Books)
async def get_a_book(book_id: str, session: AsyncSession = Depends(get_session)) -> dict:
    # for book in books:
    #     if book["id"] == book_id:
    #         return book
    book = await book_service.get_book(book_id, session)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book

@book_router.patch("/{book_id}", response_model=Books)
async def update_a_book(book_id: str, update_book: BookUpdate, session: AsyncSession = Depends(get_session)) -> dict:
    # for book in books:
    #     if book["id"] == book_id:
    #         book['title'] = update_book.title
    #         book['author'] = update_book.author
    #         book['publisher'] = update_book.publisher
    #         book['page_count'] = update_book.page_count
    #         book['language'] = update_book.language
    #         return book

    updated_book = await book_service.update_book(book_id, update_book, session)
    if updated_book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return updated_book

@book_router.delete("/{book_id}", status_code= status.HTTP_204_NO_CONTENT)
async def delete_a_book(book_id: str, session: AsyncSession = Depends(get_session)):
    # for book in books:
    #     if book["id"] == book_id:
    #         books.remove(book)
    #         return {}
    book_to_delete = await book_service.get_book(book_id, session)
    if book_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    await book_service.delete_book(book_id, session)
    return {}