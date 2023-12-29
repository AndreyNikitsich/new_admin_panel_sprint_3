from typing import Any

from storages.base_storage import BaseStorage


class State:
    """Класс для работы с состояниями."""

    def __init__(self, storage: BaseStorage) -> None:
        self.storage = storage
        self._state = None

    def set_state(self, key: str, value: Any) -> None:
        """Установить состояние для определённого ключа."""
        if self._state is None:
            self._state = self.storage.retrieve_state()

        self._state[key] = value
        self.storage.save_state(self._state)

    def get_state(self, key: str) -> Any:
        """Получить состояние по определённому ключу."""
        if self._state is None:
            self._state = self.storage.retrieve_state()
        return self._state.get(key, None)
