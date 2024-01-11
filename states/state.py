from typing import Any

from storages.base_storage import BaseStorage


class State:
    uncommitted_prefix = "_uncommitted_"

    def __init__(self, storage: BaseStorage) -> None:
        self.storage = storage
        self._state = self.storage.retrieve_state()

    def set_state_bulk(self, state: dict[str, Any], uncommitted=False) -> None:
        if uncommitted:
            state = {self.uncommitted_prefix + k: v for k, v in state.items()}

        self._state.update(state)
        self.storage.save_state(self._state)

    def commit_state(self) -> None:
        uncommitted_keys = [key for key in self._state.keys() if key.startswith(self.uncommitted_prefix)]
        for key in uncommitted_keys:
            value = self._state[key]
            new_key = key[len(self.uncommitted_prefix):]
            self._state[new_key] = value
            del self._state[key]
        self.storage.save_state(self._state)

    def get_state(self, key: str) -> Any:
        return self._state.get(key, None)
