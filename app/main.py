from fastapi import FastAPI

from app.routers import products, category

app = FastAPI()

@app.get('/')
async def welcome() -> dict:
    return {'message': 'E-Commerce APP'}

app.include_router(category.router)
app.include_router(products.router)
