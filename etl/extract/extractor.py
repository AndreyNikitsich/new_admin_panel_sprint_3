import logging
from typing import Generator, Type
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
        conn: psycopg.Connection,
        state: State,
        table_watcher_classes: list[Type[AbstractUpdatesWatcher]] | None = None,
    ):
        self._conn = conn
        self._state = state
        self._watcher_objects = []

        if table_watcher_classes is not None:
            self._watcher_objects = [tw_class(self._conn, self._state) for tw_class in table_watcher_classes]

    def _get_film_ids_for_update(self) -> list[UUID]:
        unique_film_ids = set()
        for watcher in self._watcher_objects:
            unique_film_ids.update(watcher.get_films_for_update())
        return sorted(unique_film_ids)

    def _load_films_info(self, ids: list[UUID]) -> Batch:
        query = _build_load_film_info_query(len(ids))
        with self._conn.cursor(row_factory=class_row(FilmRow)) as cur:
            cur.execute(query, ids)
            data = cur.fetchall()
        return data

    @backoff.on_exception(backoff.expo, psycopg.OperationalError, max_time=settings.others.postgres_backoff_max_time)
    def extract_films_batch(self, batch_size: int = 100) -> Generator[Batch, None, None]:
        film_ids = self._get_film_ids_for_update()
        for batch in range(0, len(film_ids), batch_size):
            ids_batch = list(film_ids[batch : batch + batch_size])
            yield self._load_films_info(ids_batch)

    @classmethod
    def get_object(cls, conn: psycopg.Connection, state: State) -> "Extractor":
        table_watcher_classes = [PersonUpdatesWatcher, GenreUpdatesWatcher, FilmWorkUpdatesWatcher]
        return Extractor(conn, state, table_watcher_classes)
