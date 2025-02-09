from fastapi import APIRouter

router = APIRouter(prefix="/products", tags=["products"])


@router.get('/')
async def get_all_products():
    ...

@router.post('/')
async def create_product():
    ...

@router.get('/{category_slug}')
async def get_product_by_category():
    ...

@router.get('/detail/{product_slug}')
async def product_detail():
    ...

@router.put('/{product_slug}')
async def update_product():
    ...

@router.delete('/')
async def delete_product():
    ...
