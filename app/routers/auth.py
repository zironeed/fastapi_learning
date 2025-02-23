from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import select, insert
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from app.models.user import User
from app.schemas import CreateUser
from app.backend.db_depends import get_db


router = APIRouter(prefix='/auth', tags=['auth'])
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
security = HTTPBasic


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_user(db: Annotated[AsyncSession, Depends(get_db)], user_data: CreateUser):
    await db.execute(insert(User).values(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        username=user_data.username,
        email=user_data.email,
        hashed_password=bcrypt_context.hash(user_data.password)
    ))
    await db.commit()
    return {
        'message': 'created.',
        'status': status.HTTP_201_CREATED
    }


async def get_current_username(
        db: Annotated[AsyncSession, Depends(get_db)], credentials: HTTPBasicCredentials = Depends(security)
):
    user = await db.scalar(select(User).where(User.username == credentials.username))
    if not user or not bcrypt_context.verify(credentials.password, User.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return user


@router.get('/users/me')
async def read_current_user(user: dict = Depends(get_current_username)):
    return {
        'User': user
    }
