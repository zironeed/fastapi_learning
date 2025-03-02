from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, insert, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.backend.db_depends import get_db
from app.models import Review, Rating, Product
from app.routers.auth import get_current_user
from app.schemas import CreateReview

router = APIRouter(prefix='/reviews', tags=['reviews'])


@router.get('/')
async def all_reviews(db: Annotated[AsyncSession, Depends(get_db)]):
    reviews = await db.scalars(
        select(Review)
        .where(Review.is_active.is_(True))
        .options(selectinload(Review.rating))
    )
    reviews = reviews.all()

    if not reviews:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There are no reviews.'
        )

    return reviews


@router.get('/{product_slug}')
async def products_reviews(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str):
    product: Product = await db.scalar(select(Product).where(
        and_(Product.slug == product_slug, Product.is_active.is_(True))
    ))
    if product:
        reviews = await db.scalars(
            select(Review).join(Rating).where(
                and_(Review.is_active.is_(True), Review.product_id == product.id)
            ).options(selectinload(Review.rating))
        )
        reviews = reviews.all()
        if reviews:
            return reviews
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There are no reviews.'
        )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail='There is no such product.'
    )


@router.post('/')
async def add_review(db: Annotated[AsyncSession, Depends(get_db)], review_: CreateReview,
                     get_user: Annotated[dict, Depends(get_current_user)]):
    if get_user.get('is_admin') or get_user.get('is_customer'):
        product: Product = await db.scalar(select(Product).where(and_(Product.id == review_.product_id,
                                                                      Product.is_active.is_(True))))
        if product:

            rating_id = await db.execute(insert(Rating).values(
                grade=review_.grade,
                product_id=review_.product_id,
                user_id=get_user.get('id')
            ).returning(Rating.id))
            rating_id = rating_id.scalar()
            await db.execute(insert(Review).values(
                rating_id=rating_id,
                product_id=review_.product_id,
                comment=review_.comment,
                user_id=get_user.get('id')
            ))

            products_ratings = await db.scalars(select(Rating).where(
                Rating.product_id == product.id and Rating.is_active is True
            ))
            grades = [rating.grade for rating in products_ratings]
            product.rating = round(sum(grades) / len(grades), 2)
            await db.commit()

            return {
                'status_code': status.HTTP_201_CREATED,
                'detail': 'Created.'
            }

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no such product.'
        )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail='Not enough permissions.'
    )


@router.delete('/')
async def delete_review(db: Annotated[AsyncSession, Depends(get_db)], review_id: int,
                        get_user: Annotated[dict, Depends(get_current_user)]):
    if get_user.get('is_admin'):
        review = await db.scalar(select(Review).where(
            and_(Review.id == review_id, Review.is_active.is_(True))
        ).options(
            selectinload(Review.rating)
        ))

        if review:
            review.is_active, review.rating.is_active = False, False
            await db.commit()

            return {
                'status_code': status.HTTP_204_NO_CONTENT,
                'detail': 'Deleted.'
            }
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no such review.'
        )
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail='Not enough permissions.'
    )
