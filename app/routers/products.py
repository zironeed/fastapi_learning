from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from slugify import slugify
from sqlalchemy import select, insert, update
from sqlalchemy.orm import Session
from starlette import status

from app.backend.db_depends import get_db
from app.models import Product, Category
from app.schemas import CreateProduct

router = APIRouter(prefix="/products", tags=["products"])


@router.get('/')
async def get_all_products(db: Annotated[Session, Depends(get_db)]):
    products = db.scalars(select(Product).where(Product.is_active == True, Product.stock > 0)).all()
    if products:
        return products
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='There are no product')


@router.post('/')
async def create_product(db: Annotated[Session, Depends(get_db)], product: CreateProduct):
    db.execute(insert(Product).values(
        name=product.name,
        description=product.description,
        price=product.price,
        image_url=product.image_url,
        stock=product.stock,
        category_id=product.category,
        slug=slugify(product.name),
        rating=0.0
    ))
    db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }


@router.get('/{category_slug}')
async def get_product_by_category(db: Annotated[Session, Depends(get_db)], category_slug: str):
    cats = [db.scalar(select(Category).where(Category.slug == category_slug)).id]
    if cats:
        categories = db.scalars(select(Category).where(Category.parent_id == cats[0])).all()
        if categories:
            cats += [cat.id for cat in categories if cat.is_active]
        products = db.scalars(select(Product).where(
            Product.category_id.in_(cats), Product.is_active == True, Product.stock > 0)).all()
        if products:
            return products
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found.')


@router.get('/detail/{product_slug}')
async def product_detail(db: Annotated[Session, Depends(get_db)], product_slug: str):
    product = db.scalar(select(Product).where(Product.slug == product_slug))
    if product:
        return product
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found.')


@router.put('/{product_slug}')
async def update_product(db: Annotated[Session, Depends(get_db)], product_slug: str, product: CreateProduct):
    product_ = db.scalar(select(Product).where(Product.slug == product_slug))
    if product_:
        db.execute(update(Product).where(Product.id == product_.id).values(
            **product.dict(),
            slug=slugify(product.name),
            rating=product_.rating
        ))
        db.commit()
        return {
            'status_code': status.HTTP_200_OK,
            'transaction': 'Successful.'
        }
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found.')


@router.delete('/')
async def delete_product(db: Annotated[Session, Depends((get_db))], product_slug: str):
    product = db.scalar(select(Product).where(Product.slug == product_slug))
    if product:
        db.execute(update(Product).where(Product.slug==product_slug).values(is_active=False))
        db.commit()
        return {
            'status_code': status.HTTP_200_OK,
            'transaction': 'Deleted.'
        }
    raise HTTPException(status_code=404, detail="Product not found")
