import logging
from typing import Dict, Optional, List, Union
import json
import asyncio
from functools import wraps

from fastapi.exceptions import HTTPException
from redis import Redis
from redis.asyncio import from_url
from redis.exceptions import ConnectionError, WatchError
from redis.asyncio.client import Pipeline

from app import settings

logger = logging.getLogger(__name__)

connection_url = f"redis://{settings.REDIS_URL}:{settings.REDIS_URL}?decode_responses=True"
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
    

async def redis_transaction_with_retry(func):
    @wraps(func)
    async def wrapper(cls, *args, **kwargs):
        retry_count = 0
        max_retries = 5

        record_type = kwargs.get("type")
        record_id = kwargs.get("id")
        name = f"{record_type}:{record_id}"

        while retry_count < max_retries:
            try:
                async with r.pipeline(transaction=True) as pipe:
                    await pipe.watch(name)
                    result = await func(cls, pipe, *args, **kwargs)
                    if pipe.watching:
                        await pipe.execute()
                    return result
            except WatchError:
                retry_count += 1
                if retry_count >= max_retries:
                    logger.exception(f"Watch error: failed to execute '{func.__name__}' on record {name} after {max_retries} retries.")
                    break

                await asyncio.sleep(0.1 * (2 ** retry_count))
                continue

            except Exception as e:
                logger.exception(f"Error during '{func.__name__}' on record {name}: {e}")
                break
        
    return wrapper



class RedisInterface:
    @classmethod
    async def get_record(cls, type: str, id: str, key: Optional[str]=None) -> Optional[dict]:
        try:
            name = f"{type}:{id}"
            if key:
                data = await r.hget(name=name, key=key)
                return {key: data}
            return await r.hgetall(name=name)
        except Exception as e:
            logger.exception(f"Error: failed to get record {type}:{id}: {e}")
            return None
        
    @classmethod
    async def record_exists(cls, type: str, id: str) -> bool:
        try:
            name = f"{type}:{id}"
            return await r.exists(name) == 1
        except Exception as e:
            logger.exception(f"Error: failed to check record existence {type}:{id}: {e}")
            return False

    @classmethod
    @redis_transaction_with_retry
    async def create_record(cls, pipe: Pipeline, type: str, id: str, data: Dict[str, Union[str, dict, int]], expire: int=None) -> None:
        name = f"{type}:{id}"

        if await pipe.exists(name):
            logger.warning(f"Record {name} already exists")
            pipe.unwatch()
            return

        store_mapping = {
            key: json.dumps(value) if isinstance(value, dict) else str(value)
            for key, value in data.items()
        }
        
        pipe.multi()
        pipe.hset(name=name, mapping=store_mapping)
        if expire is not None:
            pipe.expire(name=name, time=expire)

    @classmethod
    async def modify_record(cls, pipe: Pipeline, type: str, id: str, data: Dict[str, Union[str, dict, int]], expire: int=None) -> None:
        name = f"{type}:{id}"

        if not await pipe.exists(name):
            logger.warning(f"Record {name} does not exist")
            pipe.unwatch()
            return
        
        store_mapping = {
            key: json.dumps(value) if isinstance(value, dict) else str(value)
            for key, value in data.items()
        }

        pipe.multi()
        pipe.hset(name=name, mapping=store_mapping)
        if expire is not None:
            pipe.expire(name=name, time=expire)

    @classmethod
    @redis_transaction_with_retry
    async def delete_record_key(cls, pipe: Pipeline, type: str, id: str, key: str):
        name = f"{type}:{id}"
        if not await pipe.hexists(name, key):
            logger.warning(f"Field '{key}' in record {name} does not exist. Cannot delete.")
            pipe.unwatch()
            return
            
        pipe.multi()
        pipe.hdel(name, key)

    @classmethod
    @redis_transaction_with_retry
    async def delete_record(cls, pipe: Pipeline, type: str, id: str):
        name = f"{type}:{id}"
        if not await pipe.exists(name):
            logger.warning(f"Record {name} does not exist. Cannot delete.")
            pipe.unwatch()
            return

        pipe.multi()
        pipe.delete(name)