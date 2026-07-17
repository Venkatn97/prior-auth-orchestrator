import json
import redis
import time
from typing import Optional
from shared.config import settings

redis_client=redis.from_url(settings.redis_url,decode_responses=True)

def set_cache(key:str, value:dict, ttl_seconds:int=300)->None:
    redis_client.setex(key,ttl_seconds, json.dumps(value))

def get_cache(key:str)->Optional[dict]:
    raw=redis_client.get(key)
    if raw is None:
        return None
    return json.loads(raw)

def delete_cache(key:str)->None:
    redis_client.delete(key)


def get_or_compute(key:str,compute_fn,ttl_seconds:int=300)->dict:
    cached=get_cache(key)
    if cached is not None:
        return cached
    
    lock_key=f"lock:{key}"
    got_lock=redis_client.set(lock_key,"1",nx=True,ex=10)

    if got_lock:
        try:
            result=compute_fn()
            set_cache(key,result, ttl_seconds)
            return result
        finally:
            redis_client.delete(lock_key)
    
    else:
        for _ in range(20):
            time.sleep(0.25)
            cached= get_cache(key)
            if cached is not None:
                return cached
        
        return compute_fn()