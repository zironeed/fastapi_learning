from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated
from sqlalchemy import insert, select, update
from slugify import slugify

from app.backend.db_depends import get_db
from app.schemas import CreateCategory
from app.models.category import Category

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get('/')
async def get_all_categories(db: Annotated[Session, Depends(get_db)]):
    categories = db.scalars(select(Category).where(Category.is_active == True)).all()
    return categories


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_category(db: Annotated[Session, Depends(get_db)], create_category: CreateCategory):
    db.execute(insert(Category).values(name=create_category.name,
                                       parent_id=create_category.parent_id,
                                       slug=slugify(create_category.name)))
    db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }


@router.put('/')
async def update_category(db: Annotated[Session, Depends(get_db)], category_id: int, update_category: CreateCategory):
    category = db.scalar(select(Category).where(Category.id == category_id))
    if category:
        db.execute(update(Category).where(Category.id == category_id).values(
            name=update_category.name,
            slug=slugify(update_category.name),
            parent_id=update_category.parent_id
        ))
        db.commit()
        return {
            'status_code': status.HTTP_200_OK,
            'transaction': 'Successful.'
        }
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")


@router.delete('/')
async def delete_category(db: Annotated[Session, Depends((get_db))], category_id: int):
    category = db.scalar(select(Category).where(Category.id == category_id))
    if category:
        db.execute(update(Category).where(Category.id == category_id).values(is_active=False))
        db.commit()
        return {
            'status_code': status.HTTP_200_OK,
            'transaction': 'Deleted.'
        }
    raise HTTPException(status_code=404, detail="Category not found")
