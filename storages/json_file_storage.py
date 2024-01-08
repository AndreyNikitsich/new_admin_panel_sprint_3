import datetime
import json
from json import JSONDecodeError
from typing import Any, Dict
from uuid import UUID

from .base_storage import BaseStorage


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        elif isinstance(obj, UUID):
            return str(obj)
        return super().default(obj)


class JsonFileStorage(BaseStorage):
    def __init__(self, file_path: str = "state.json") -> None:
        self.file_path = file_path

    def save_state(self, state: Dict[str, Any]) -> None:
        with open(self.file_path, "w") as f:
            f.write(json.dumps(state, sort_keys=True, indent=4, cls=CustomJSONEncoder))

    def retrieve_state(self) -> Dict[str, Any]:
        try:
            with open(self.file_path) as f:
                state = json.load(f)
        except (FileNotFoundError, JSONDecodeError):
            state = {}
        return state
