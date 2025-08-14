from fastapi import status
from fastapi.exceptions import HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
import logging
from src.db.models import Review
from src.auth.service import UserService
from src.books.service import BookService
from .schemas import CreateReview

user_service = UserService()
book_service = BookService()

class ReviewService:
    async def add_review_to_book(self, user_email: str, book_uid: str, review_data: CreateReview, session: AsyncSession):
        try:
            book = await book_service.get_book(book_uid, session)
            if book is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
            user = await user_service.get_user_by_email(user_email, session)
            if user is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            
            review_data_dict = review_data.model_dump()
            new_review = Review(**review_data_dict)
            new_review.user = user
            new_review.book = book
            
            session.add(new_review)
            await session.commit()
            return new_review
        except Exception as e:
            logging.exception(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
    async def get_review_by_id(self, review_id: str, session: AsyncSession):
        try:
            statement = select(Review).where(Review.uid == review_id)
            result = await session.exec(statement)
            return result.first()
        except Exception as e:
            logging.exception(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
    async def delete_review_by_id(self, review_id: str, session: AsyncSession):
        try:
            review_to_delete = await self.get_review_by_id(review_id, session)
            if review_to_delete is not None:
                await session.delete(review_to_delete)
                await session.commit()
                return {}
            else:
                return None
        except Exception as e:
            logging.exception(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))