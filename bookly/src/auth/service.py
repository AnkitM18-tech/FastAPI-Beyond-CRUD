from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.models import User
from .schemas import CreateUser
from .utils import generate_hash

class UserService:
    async def get_user_by_email(self, email: str, session: AsyncSession):
        statement = select(User).where(User.email == email)
        result = await session.exec(statement)
        return result.first()
    
    async def user_exists(self, email: str, session: AsyncSession):
        user = await self.get_user_by_email(email, session)
        return user is not None
    
    async def create_user(self, user_data: CreateUser, session: AsyncSession):
        user = user_data.model_dump()
        new_user = User(**user)
        new_user.password = generate_hash(new_user.password)
        new_user.role = "user"
        session.add(new_user)
        await session.commit()
        return new_user