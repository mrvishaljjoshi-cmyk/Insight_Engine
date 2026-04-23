import functools
import json
from app.core.redis import redis_client
from typing import Any, Callable

def cache_response(ttl: int = 60):
    """
    Decorator to cache broker API responses in Redis.
    Key is based on user_id, broker_name, and the method name.
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            # Try to find user_id from self (Broker instance)
            # In our Broker implementations, we can store user_id during init
            user_id = getattr(self, 'user_id', 'global')
            
            cache_key = f"broker_cache:{user_id}:{func.__name__}:{self.__class__.__name__}:{args}:{kwargs}"
            
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            result = func(self, *args, **kwargs)
            
            # If result is a list of Pydantic models, convert to dict
            if isinstance(result, list):
                serializable_result = [item.model_dump() if hasattr(item, 'model_dump') else item for item in result]
            elif hasattr(result, 'model_dump'):
                serializable_result = result.model_dump()
            else:
                serializable_result = result
                
            redis_client.setex(cache_key, ttl, json.dumps(serializable_result))
            return result
        return wrapper
    return decorator
