from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.models import User
from src.db.main import get_session
from src.auth.dependencies import get_current_user
from .schemas import CreateReview, Review
from .service import ReviewService
from src.errors import ReviewNotFound, InsufficientPermission

review_router = APIRouter()
review_service = ReviewService()

@review_router.post("/book/{book_id}", status_code= status.HTTP_201_CREATED, response_model=Review)
async def add_review_to_book(book_id: str, review_data: CreateReview, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    new_review = await review_service.add_review_to_book(
        user_email= current_user.email,
        book_uid= book_id,
        review_data= review_data,
        session= session
    )
    return new_review

@review_router.get("/{review_id}", response_model=Review)
async def get_a_review_by_id(review_id: str, session: AsyncSession = Depends(get_session)):
    review = await review_service.get_review_by_id(review_id, session)
    if review is not None:
        return review
    raise ReviewNotFound()

@review_router.delete("/{review_id}", status_code= status.HTTP_204_NO_CONTENT)
async def delete_a_review_by_id(review_id: str, session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    review = await review_service.get_review_by_id(review_id, session)
    if current_user.uid != review.user_uid:
        raise InsufficientPermission()
    if review is not None:
        await review_service.delete_review_by_id(review_id, session)
        return {}
    raise ReviewNotFound()