import json
from json import JSONDecodeError
from typing import Any, Dict

from .base_storage import BaseStorage


class JsonFileStorage(BaseStorage):
    """Реализация хранилища, использующего локальный файл.

    Формат хранения: JSON
    """

    def __init__(self, file_path: str = "state.json") -> None:
        self.file_path = file_path

    def save_state(self, state: Dict[str, Any]) -> None:
        """Сохранить состояние в хранилище."""
        with open(self.file_path, "w") as f:
            f.write(json.dumps(state, sort_keys=True, indent=4))

    def retrieve_state(self) -> Dict[str, Any]:
        """Получить состояние из хранилища."""
        try:
            with open(self.file_path) as f:
                state = json.load(f)
        except (FileNotFoundError, JSONDecodeError):
            state = {}
        return state
