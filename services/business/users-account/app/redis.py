import logging
from typing import Dict, Optional, List, Union
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
    @classmethod
    async def get_record(cls, type: str, id: str, key: Optional[str]=None) -> Optional[dict]:
        try:
            async with r.pipeline(transaction=True) as pipe:
                name = f"{type}:{id}"
                if key:
                    data = await pipe.hget(name=name, key=key)
                    return {key: data}
                else:
                    data = await pipe.hgetall(name=name)
                    return data
                # return json.loads(data) if data is not None else data
        except WatchError as e:
            logger.exception(f"Watch error: failed to get record {type}:{id}: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: failed to decode record {type}:{id}: {e}")
            return None
        except Exception as e:
            logger.exception(f"Error: failed to get record {type}:{id}: {e}")
            return None

    @classmethod
    async def create_record(cls, type: str, id: str, data: Dict[str, Union[str, dict, int]], expire: int=None) -> None:
        retry_count = 0
        max_retries = 5
        name = f"{type}:{id}"

        store_mapping = {
            key: json.dumps(value) if isinstance(value, dict) else str(value)
            for key, value in data.items()
        }

        while retry_count < max_retries:
            try:
                async with r.pipeline(transaction=True) as pipe:
                    name = f"{type}:{id}"
                    await pipe.watch(name)
                    if await pipe.exists(name):
                        await pipe.unwatch()
                        return
                    
                    pipe.multi()
                    pipe.hset(name=name, mapping=store_mapping)
                    if expire is not None:
                        pipe.expire(name=name, time=expire)
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

    @classmethod
    async def modify_record(cls, type: str, id: str, key: str = None, value: Union[dict, str] = None) -> None:
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

    @classmethod
    async def delete_record_key(cls, type: str, id: str, key: str) -> None:
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

    @classmethod
    async def delete_record(cls, type: str, id: str) -> None:
        retry_count = 0
        max_retries = 5
        while retry_count < max_retries:
            try:
                name = f"{type}:{id}"
                if not await cls.record_exist(type=type, id=id):
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

    @classmethod
    async def record_exist(cls, type: str, id: str) -> bool:
        try:
            async with r.pipeline(transaction=True) as pipe:
                name = f"{type}:{id}"
                data = await pipe.exists(name)
                return data == 1
        except WatchError as e:
            logger.exception(f"Watch error while checking record existence: {e}")
            return False
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            return False

