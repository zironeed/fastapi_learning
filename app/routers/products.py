from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from slugify import slugify
from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.backend.db_depends import get_db
from app.models import Product, Category
from app.schemas import CreateProduct

router = APIRouter(prefix="/products", tags=["products"])


@router.get('/')
async def get_all_products(db: Annotated[AsyncSession, Depends(get_db)]):
    products = await db.scalars(select(Product).where(Product.is_active == True, Product.stock > 0))
    if products:
        return products.all()
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='There are no product')


@router.post('/')
async def create_product(db: Annotated[AsyncSession, Depends(get_db)], product: CreateProduct):
    await db.execute(insert(Product).values(
        name=product.name,
        description=product.description,
        price=product.price,
        image_url=product.image_url,
        stock=product.stock,
        category_id=product.category_id,
        slug=slugify(product.name),
        rating=0.0
    ))
    await db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }


@router.get('/{category_slug}')
async def get_product_by_category(db: Annotated[AsyncSession, Depends(get_db)], category_slug: str):
    main_cat = await db.scalar(select(Category).where(Category.slug == category_slug))
    if main_cat:
        cats = [main_cat.id]
        categories = await db.scalars(select(Category).where(Category.parent_id == cats[0]))
        if categories:
            cats += [cat.id for cat in categories.all() if cat.is_active]
        products = await db.scalars(select(Product).where(
            Product.category_id.in_(cats), Product.is_active == True, Product.stock > 0))
        if products:
            return products.all()
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found.')


@router.get('/detail/{product_slug}')
async def product_detail(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str):
    product = await db.scalar(select(Product).where(Product.slug == product_slug))
    if product:
        return product
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found.')


@router.put('/{product_slug}')
async def update_product(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str, product: CreateProduct):
    product_ = await db.scalar(select(Product).where(Product.slug == product_slug))
    if product_:
        product_.name = product.name
        product_.description = product.description
        product_.price = product.price
        product_.image_url = product.image_url
        product_.stock = product.stock
        product_.category_id = product.category_id
        product_.slug = slugify(product.name)
        await db.commit()
        return {
            'status_code': status.HTTP_200_OK,
            'transaction': 'Successful.'
        }
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found.')


@router.delete('/')
async def delete_product(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str):
    product = await db.scalar(select(Product).where(Product.slug == product_slug))
    if product:
        product.is_active = False
        await db.commit()
        return {
            'status_code': status.HTTP_200_OK,
            'transaction': 'Deleted.'
        }
    raise HTTPException(status_code=404, detail="Product not found")
