from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from slugify import slugify
from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.routers.auth import get_current_user
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
async def create_product(db: Annotated[AsyncSession, Depends(get_db)], create_product: CreateProduct,
                         get_user: Annotated[dict, Depends(get_current_user)]):
    if get_user.get('is_supplier') or get_user.get('is_admin'):
        category = await db.scalar(select(Category).where(Category.id == create_product.category))
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='There is no category found'
            )
        await db.execute(insert(Product).values(name=create_product.name,
                                                description=create_product.description,
                                                price=create_product.price,
                                                image_url=create_product.image_url,
                                                stock=create_product.stock,
                                                category_id=create_product.category,
                                                rating=0.0,
                                                slug=slugify(create_product.name),
                                                supplier_id=get_user.get('id')))
        await db.commit()
        return {
            'status_code': status.HTTP_201_CREATED,
            'transaction': 'Successful'
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You have not enough permission for this action'
        )


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


@router.put('/detail/{product_slug}')
async def update_product(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str,
                         update_product_model: CreateProduct, get_user: Annotated[dict, Depends(get_current_user)]):
    if get_user.get('is_supplier') or get_user.get('is_admin'):
        product_update = await db.scalar(select(Product).where(Product.slug == product_slug))
        if product_update is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='There is no product found'
            )
        if get_user.get('id') == product_update.supplier_id or get_user.get('is_admin'):
            category = await db.scalar(select(Category).where(Category.id == update_product_model.category))
            if category is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail='There is no category found'
                )
            product_update.name = update_product_model.name
            product_update.description = update_product_model.description
            product_update.price = update_product_model.price
            product_update.image_url = update_product_model.image_url
            product_update.stock = update_product_model.stock
            product_update.category_id = update_product_model.category
            product_update.slug = slugify(update_product_model.name)

            await db.commit()
            return {
                'status_code': status.HTTP_200_OK,
                'transaction': 'Product update is successful'
            }
        else:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='You have not enough permission for this action'
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You have not enough permission for this action'
        )


@router.delete('/')
async def delete_product(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str,
                         get_user: Annotated[dict, Depends(get_current_user)]):
    product_delete = await db.scalar(select(Product).where(Product.slug == product_slug))
    if product_delete is None:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='There is no product found'
             )
    if get_user.get('is_supplier') or get_user.get('is_admin'):
        if get_user.get('id') == product_delete.supplier_id or get_user.get('is_admin'):
            product_delete.is_active = False
            await db.commit()
            return {
                'status_code': status.HTTP_200_OK,
                'transaction': 'Product delete is successful'
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='You have not enough permission for this action'
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You have not enough permission for this action'
        )
