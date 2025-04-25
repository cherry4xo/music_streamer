import os
import uuid
import logging

from tortoise.contrib.fastapi import register_tortoise
from aerich import Command
from fastapi import FastAPI

from app import settings

logger = logging.getLogger(__name__)

def get_tortoise_config() -> dict:
    app_list = ["app.models", "aerich.models"]
    config = {
        "connections": settings.DB_CONNECTIONS,
        "apps": {
            "models": {
                "models": app_list,
                "default_connection": "default"
            }
        }
    }   
    return config

TORTOISE_ORM = get_tortoise_config()

def register_db(app: FastAPI, db_url: str = None) -> None:
    db_url = db_url or settings.DB_URL
    register_tortoise(
        app,
        config=TORTOISE_ORM,
        generate_schemas=False,
        add_exception_handlers=True
    )

async def upgrade_db():
    command = Command(tortoise_config=TORTOISE_ORM, app="models", location="./migrations")
    print(TORTOISE_ORM)
    if not os.path.exists("./migrations/models"):
        await command.init_db(safe=True)
    await command.init()

async def init(app: FastAPI):
    await upgrade_db(app)
    register_db(app)
    logger.debug("Connected to db")