from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" ALTER COLUMN "first_name" DROP NOT NULL;
        ALTER TABLE "users" ALTER COLUMN "display_name" DROP NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" ALTER COLUMN "first_name" SET NOT NULL;
        ALTER TABLE "users" ALTER COLUMN "display_name" SET NOT NULL;"""
