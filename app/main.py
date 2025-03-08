import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request

from app.routers import products, category, auth, permissions, reviews
from middleware import TimingMiddleware

app = FastAPI(title='Ecommerce API v1',
              description='Educational project about an online store (ver. 1)')

@app.middleware("http")
async def modify_request_response_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    print(f"Request duration: {duration:.10f} seconds")
    return response

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=["*"]
)
app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(SessionMiddleware, secret_key="7UzGQS7woBazLUtVQJG39ywOP7J7lkPkB0UmDhMgBR8=")
app.add_middleware(TimingMiddleware)


app.include_router(category.router)
app.include_router(products.router)
app.include_router(auth.router)
app.include_router(permissions.router)
app.include_router(reviews.router)

app.mount('/v1', app)


@app.get('/')
async def welcome() -> dict:
    return {'message': 'E-Commerce APP'}


@app.get("/create_session")
async def session_set(request: Request):
    request.session["my_session"] = "1234"
    return 'ok'


@app.get("/read_session")
async def session_info(request: Request):
    my_var = request.session.get("my_session")
    return my_var


@app.get("/delete_session")
async def session_delete(request: Request):
    my_var = request.session.pop("my_session")
    return my_var
