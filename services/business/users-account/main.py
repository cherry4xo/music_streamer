from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from prometheus_fastapi_instrumentator import Instrumentator

from app.db import init
from app import settings
from app.settings import EventTypes
from app.routes import router as login_router
from app.logger import setup_logging, LoggingMiddleware
from app.models import User
from app.kafka_interface import KafkaInterface


def init_middlewares(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS
    )
    app.add_middleware(LoggingMiddleware)


logger = setup_logging("account-service")
app = FastAPI(root_path=settings.ROOT_PATH)
instrumentator = Instrumentator().instrument(app=app)

async def handle_kafka_message(event: dict):
    event_type = event.get("event_type")

    match event_type:
        case EventTypes.USER_CREATED.value:
            user_uuid = event.get("uuid")
            username = event.get("username")
            email = event.get("email")
            logger.info(f"Handling user_created event for user_uuid: {user_uuid}")

            await User.create(uuid=user_uuid, username=username, email=email)
            logger.info(f"User created: {user_uuid}")
        case _:
            logger.info(f"Unknown event type: {event_type}")

kafka_client = KafkaInterface(
    kafka_url=settings.KAFKA_URL,
    consume_topics=settings.KAFKA_CONSUME_TOPICS,
    message_handler=handle_kafka_message,
)


main_app_lifespan = app.router.lifespan_context
@asynccontextmanager
async def lifespan_wrapper(app):
    await init(app=app)
    await kafka_client.start()
    instrumentator.expose(app)
    async with main_app_lifespan(app) as maybe_state:
        yield maybe_state
        await kafka_client.stop()

app.router.lifespan_context = lifespan_wrapper
init_middlewares(app)
app.include_router(login_router, tags=["root"])