from pydantic import BaseModel, Field
import uuid
from datetime import datetime
from typing import List
from src.books.schemas import Books

class CreateUser(BaseModel):
    username: str = Field(max_length=20)
    email: str = Field(max_length=40)
    password: str = Field(min_length=6)
    first_name: str = Field(max_length=20)
    last_name: str = Field(max_length=20)

# can make use of existing User Model in models
class UserModel(BaseModel):
    uid: uuid.UUID
    username: str
    email: str
    password: str = Field(exclude=True)
    first_name: str
    last_name: str
    created_at: datetime
    updated_at: datetime 
    is_verified: bool
    books: List[Books]

class UserLogin(BaseModel):
    email: str = Field(max_length=40)
    password: str = Field(min_length=6)