import datetime
from typing import Any, Dict

import redis

from .base_storage import BaseStorage


class RedisStorage(BaseStorage):
    _state_key = "app_state"

    def __init__(self, redis_client: redis.Redis) -> None:
        self._client = redis_client

    def save_state(self, state: Dict[str, Any]) -> None:
        encoded_state = {}
        for key, value in state.items():
            if isinstance(value, (datetime.datetime, datetime.date)):
                encoded_state[key] = value.isoformat()
        self._client.hset(self._state_key, mapping=encoded_state)

    def retrieve_state(self) -> Dict[str, Any]:
        state = self._client.hgetall(self._state_key)
        return state
