from fastapi import APIRouter

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get('/')
async def get_all_categories():
    ...

@router.post('/')
async def create_category():
    ...

@router.put('/')
async def update_category():
    ...

@router.delete('/')
async def delete_category():
    ...
