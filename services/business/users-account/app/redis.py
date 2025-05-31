import logging
from typing import Optional, List, Union
import json
import asyncio

from fastapi.exceptions import HTTPException
from redis import Redis
from redis.asyncio import from_url
from redis.exceptions import ConnectionError, WatchError

from app import settings

logger = logging.getLogger(__name__)

connection_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}?decode_responses=True"
r = from_url(connection_url)

async def ping_redis_connection(r: Redis):
    try:
        await r.ping()
        logger.info("Redis pinged. Successfully connected")
    except ConnectionError:
        raise HTTPException(
            status_code=500,
            detail=f"Redis error: failed to connect to redis database with url {connection_url}"
        )
    

class RedisInterface:
    def __init__(self, **kwargs):
        pass

    async def get_record(self, type: str, id: str, key: Optional[str]=None) -> Optional[dict]:
        await ping_redis_connection(r)
        try:
            async with r.pipeline(transaction=True) as pipe:
                name = f"{type}:{id}"
                await pipe.watch(name)
                if key:
                    data = await pipe.hget(name=name, key=key)
                else:
                    data = await pipe.hgetall(name=name)
                await pipe.unwatch()
                return json.loads(data) if data is not None else data
        except WatchError as e:
            logger.exception(f"Watch error: failed to get record {type}:{id}: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: failed to decode record {type}:{id}: {e}")
            return None
        except Exception as e:
            logger.exception(f"Error: failed to get record {type}:{id}: {e}")
            return None

    async def create_record(self, type: str, id: str, key: Optional[str]=None, value: Union[dict, str]=None) -> None:
        await ping_redis_connection(r)
        retry_count = 0
        max_retries = 5

        store_value = value if isinstance(value, str) else json.dumps(value)
        while retry_count < max_retries:
            try:
                async with r.pipeline(transaction=True) as pipe:
                    name = f"{type}:{id}"
                    await pipe.watch(name)
                    if key:
                        data = await pipe.hget(name=name, key=key)
                    else:
                        data = await pipe.hgetall(name=name)
                    if data:
                        await pipe.unwatch()
                        return
                    pipe.multi()
                    pipe.hset(name=name, key=key, value=store_value)
                    await pipe.execute()
                    break
            except WatchError as e:
                retry_count += 1
                if retry_count >= max_retries:
                    logger.exception(f"Watch error: failed to create record {type}:{id}: {e}")
                    break
                await asyncio.sleep(0.1 * 2 ** retry_count)
            except Exception as e:
                logger.exception(f"Error: failed to create record {type}:{id}: {e}")
                break

    async def modify_record(self, type: str, id: str, key: str = None, value: Union[dict, str] = None) -> None:
        await ping_redis_connection(r)
        retry_count = 0
        max_retries = 5

        store_value = value if isinstance(value, str) else json.dumps(value)
        while retry_count < max_retries:
            try:
                async with r.pipeline(transaction=True) as pipe:
                    name = f"{type}:{id}"
                    await pipe.watch(name)
                    if key:
                        data = await pipe.hget(name=name, key=key)
                    else:
                        data = await pipe.hgetall(name=name)
                    if not data:
                        logger.warning(f"Record {type}:{id} does not exist")
                        return
                    pipe.multi()
                    pipe.hset(name=name, key=key, value=store_value)
                    await pipe.execute()
                    break
            except WatchError as e:
                retry_count += 1
                if retry_count >= max_retries:
                    logger.exception(f"Watch error: failed to modify record {type}:{id}: {e}")
                    break
                await asyncio.sleep(0.1 * 2 ** retry_count)
            except Exception as e:
                logger.exception(f"Error while modifying record: {e}")
                break

    async def delete_record_key(self, type: str, id: str, key: str) -> None:
        await ping_redis_connection(r)
        retry_count = 0
        max_retries = 5
        while retry_count < max_retries:
            try:
                async with r.pipeline(transaction=True) as pipe:
                    name = f"{type}:{id}"
                    await pipe.watch(name)
                    data = await pipe.hget(name=name, key=key)
                    if not data:
                        await pipe.unwatch()
                        return
                    pipe.multi()
                    pipe.hdel(name, key)
                    await pipe.execute()
                    break
            except WatchError:
                retry_count += 1
                if retry_count >= max_retries:
                    logger.error(f"Failed to delete record key after {max_retries} retries")
                    break
                await asyncio.sleep(0.1 * (2 ** retry_count))
            except Exception as e:
                logger.exception(f"Error while deleting record key: {e}")
                break

    async def delete_record(self, type: str, id: str) -> None:
        await ping_redis_connection(r)
        retry_count = 0
        max_retries = 5
        while retry_count < max_retries:
            try:
                name = f"{type}:{id}"
                if not await self.record_exist(id):
                    logger.warning(f"Record {name} does not exist")
                    return
                async with r.pipeline(transaction=True) as pipe:
                    await pipe.watch(name)
                    pipe.multi()
                    pipe.delete(name)
                    await pipe.execute()
                    break
            except WatchError:
                retry_count += 1
                if retry_count >= max_retries:
                    logger.error(f"Failed to delete record after {max_retries} retries")
                    break
                await asyncio.sleep(0.1 * (2 ** retry_count))
            except Exception as e:
                logger.exception(f"Error while deleting record: {e}")
                break

    async def record_exist(self, type: str, id: str) -> bool:
        await ping_redis_connection(r)
        try:
            async with r.pipeline(transaction=True) as pipe:
                name = f"{type}:{id}"
                await pipe.watch(name)
                data = await pipe.exists(name)
                await pipe.unwatch()
                return data == 1
        except WatchError as e:
            logger.exception(f"Watch error while checking record existence: {e}")
            return False
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            return False

