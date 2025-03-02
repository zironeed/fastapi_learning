from fastapi import FastAPI

from app.routers import products, category, auth, permissions, reviews

app = FastAPI(title='Ecommerce API v1',
              description='Educational project about an online store (ver. 1)')


@app.get('/')
async def welcome() -> dict:
    return {'message': 'E-Commerce APP'}

app.include_router(category.router)
app.include_router(products.router)
app.include_router(auth.router)
app.include_router(permissions.router)
app.include_router(reviews.router)

app.mount('v1', app)
