from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from prometheus_fastapi_instrumentator import Instrumentator

from app.db import init
from app import settings
from app.routes import router as login_router
from app.logger import setup_logging, LoggingMiddleware


def init_middlewares(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS
    )
    app.add_middleware(LoggingMiddleware)


setup_logging("account-service")
app = FastAPI(root_path=settings.ROOT_PATH)
instrumentator = Instrumentator().instrument(app=app)

main_app_lifespan = app.router.lifespan_context
@asynccontextmanager
async def lifespan_wrapper(app):
    await init(app=app)
    instrumentator.expose(app)
    async with main_app_lifespan(app) as maybe_state:
        yield maybe_state

app.router.lifespan_context = lifespan_wrapper
init_middlewares(app)
app.include_router(login_router, tags=["root"])