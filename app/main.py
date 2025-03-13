import time
from datetime import datetime, timezone, timedelta
from uuid import uuid4

from celery import Celery
from celery.schedules import crontab
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from loguru import logger
from starlette.responses import JSONResponse

from app.routers import products, category, auth, permissions, reviews
from middleware import TimingMiddleware
from tasks import call_background_task


app = FastAPI(title='Ecommerce API v1',
              description='Educational project about an online store (ver. 1)')

celery = Celery(
    __name__,
    broker='redis://127.0.0.1:6379/0',
    backend='redis://127.0.0.1:6379/0',
    broker_connection_retry_on_startup=True
)
# celery -A main.celery beat --loglevel=info
# celery -A main.celery worker --loglevel=info -P gevent
# celery -A main.celery flower

celery.conf.beat_schedule = {
    'run-me-background-task': {
        'task': 'task.call_background_task',
        'schedule': 60.0,
        'args': ('Test text message',)
    }
}

# celery.conf.beat_schedule = {
#     'run-me-background-task': {
#         'task': 'task.call_background_task',
#         'schedule': crontab(hour=7, minute=0),
#         'args': ('Test text message',)
#     }
# }


@app.middleware("http")
async def log_middleware(request: Request, call_next):
    log_id = str(uuid4())
    with logger.contextualize(log_id=log_id):
        try:
            response = await call_next(request)
            if response.status_code in [401, 402, 403, 404]:
                logger.warning(f"Request to {request.url.path} failed")
            else:
                logger.info('Successfully accessed ' + request.url.path)
        except Exception as ex:
            logger.error(f"Request to {request.url.path} failed: {ex}")
            response = JSONResponse(content={"success": False}, status_code=500)
        return response
logger.add("info.log", format="Log: [{extra[log_id]}:{time} - {level} - {message}]", level="INFO", enqueue=True)

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
async def welcome(message: str) -> dict:
    call_background_task.apply_async(args=[message], countdown=60*5)
    task_datetime = datetime.now(timezone.utc) + timedelta(minutes=10)
    call_background_task.apply_async(args=[message], eta=task_datetime)
    welcome_msg()
    return {'message': 'E-Commerce APP'}


def welcome_msg():
    logger.info("welcome() called!")


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
