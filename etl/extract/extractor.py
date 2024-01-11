import logging
from typing import Any, Generator, Type
from uuid import UUID

import backoff
import psycopg
from psycopg.rows import class_row

from settings import settings
from states.state import State

from .models import Batch, FilmRow
from .query_builders import _build_load_film_info_query
from .table_watchers import AbstractUpdatesWatcher, FilmWorkUpdatesWatcher, GenreUpdatesWatcher, PersonUpdatesWatcher

logger = logging.getLogger(__name__)


class Extractor:
    def __init__(
        self,
        connection_info: dict[str, Any],
        state: State,
        table_watcher_classes: list[Type[AbstractUpdatesWatcher]] | None = None,
    ):
        self._connection_info = connection_info
        self._conn = None
        self._state = state
        self._watcher_objects = []

        if table_watcher_classes is not None:
            self._watcher_objects = [tw_class(self._state) for tw_class in table_watcher_classes]

        self._connect()

    def _get_film_ids_for_update(self) -> list[UUID]:
        unique_film_ids = set()
        for watcher in self._watcher_objects:
            unique_film_ids.update(watcher.get_films_for_update(self._conn))
        return sorted(unique_film_ids)

    def _load_films_info(self, ids: list[UUID]) -> Batch:
        query = _build_load_film_info_query(len(ids))
        with self._conn.cursor(row_factory=class_row(FilmRow)) as cur:
            cur.execute(query, ids)
            data = cur.fetchall()
        return data

    def extract_films_batch(self, batch_size: int = 100) -> Generator[Batch, None, None]:
        try:
            film_ids = self._get_film_ids_for_update()
            for batch in range(0, len(film_ids), batch_size):
                ids_batch = list(film_ids[batch : batch + batch_size])
                yield self._load_films_info(ids_batch)
        except psycopg.OperationalError:
            self._connect()

    @backoff.on_exception(backoff.expo, psycopg.OperationalError, max_time=settings.others.postgres_backoff_max_time)
    def _connect(self):
        if self._conn is not None:
            self._conn.close()
            self._conn = None
        self._conn = psycopg.connect(**self._connection_info)

    def __del__(self) -> None:
        if self._conn is not None:
            self._conn.close()

    @classmethod
    def get_object(cls, state: State) -> "Extractor":
        table_watcher_classes = [PersonUpdatesWatcher, GenreUpdatesWatcher, FilmWorkUpdatesWatcher]
        return Extractor(settings.postgres.model_dump(), state, table_watcher_classes)
