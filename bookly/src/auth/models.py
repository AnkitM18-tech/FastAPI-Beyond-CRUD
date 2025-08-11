from sqlmodel import SQLModel, Field, Column
import sqlalchemy.dialects.postgresql as pg
from datetime import datetime
import uuid

class User(SQLModel, table= True):
    __tablename__ = "users"
    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )
    username: str
    email: str
    password: str = Field(exclude=True)
    first_name: str
    last_name: str
    created_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP, 
            default=datetime.now()
        )
    )
    updated_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP, 
            default=datetime.now()
        )
    )
    is_verified: bool = Field(default=False)

    def __repr__(self):
        return f"<User ({self.username})>"