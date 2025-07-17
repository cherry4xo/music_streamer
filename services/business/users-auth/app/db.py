# app/db.py (Refactored with Retry Logic)

import os
import logging
import asyncio
from typing import Dict

from tortoise import Tortoise
from tortoise.contrib.fastapi import register_tortoise
from aerich import Command
from fastapi import FastAPI
# It's good practice to catch specific exceptions, but ConnectionRefusedError is common
# across different libraries and scenarios.
from asyncpg.exceptions import CannotConnectNowError # A specific exception for Postgres

from app import settings

logger = logging.getLogger(__name__)

# --- CONFIGURATION (No changes needed here) ---
def get_tortoise_config() -> dict:
    app_list = ["app.models", "aerich.models"]
    config = {
        "connections": {"default": settings.DB_URL}, # Ensure settings.DB_URL reads from the environment
        "apps": {
            "models": {
                "models": app_list,
                "default_connection": "default"
            }
        }
    }
    return config

TORTOISE_ORM = get_tortoise_config()

# --- NEW RESILIENT CONNECTION FUNCTION ---

async def connect_and_migrate_with_retry():
    """
    Connects to the database and runs migrations, with a retry loop
    to handle startup race conditions in a containerized environment.
    """
    max_retries = 15
    retry_delay_seconds = 5
    
    command = Command(tortoise_config=TORTOISE_ORM, app="models", location="./migrations")
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting to connect to database... (Attempt {attempt + 1}/{max_retries})")
            
            # 1. Initialize the Tortoise ORM with the config. This creates the connection pool.
            await Tortoise.init(config=TORTOISE_ORM)
            
            # 2. Initialize Aerich. This checks for the migrations table.
            await command.init()
            
            # 3. Apply all pending migrations.
            # `upgrade` is idempotent and safe to run on every startup.
            logger.info("Running database migrations...")
            await command.upgrade()
            
            logger.info("Database connection successful and migrations are up to date.")
            return  # Exit the function on success

        except (ConnectionRefusedError, TimeoutError, CannotConnectNowError) as e:
            if attempt + 1 == max_retries:
                logger.error("Failed to connect to database after all retries. Exiting.")
                raise  # Re-raise the final exception to cause the app to crash
            
            logger.warning(
                f"Database connection failed: {e}. "
                f"Postgres may not be ready yet. Retrying in {retry_delay_seconds} seconds..."
            )
            await asyncio.sleep(retry_delay_seconds)

# --- UPDATED MAIN INIT FUNCTION ---

async def init(app: FastAPI):
    """
    The main initialization function for the application's lifespan.
    """
    logger.info("Starting database initialization...")
    
    # 1. Connect to the DB and run migrations. This function will now wait
    #    patiently for the database to be ready.
    await connect_and_migrate_with_retry()
    
    # 2. Register the Tortoise handlers with the FastAPI app.
    #    This should only happen AFTER a successful connection.
    register_tortoise(
        app,
        config=TORTOISE_ORM,
        generate_schemas=False, # We've already handled schemas with Aerich
        add_exception_handlers=True
    )
    
    logger.info("Database initialization complete and exception handlers registered.")

# The old register_db and upgrade_db functions are no longer needed
# as their logic is now consolidated in connect_and_migrate_with_retry and init.