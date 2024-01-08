import abc
from datetime import datetime
from typing import Optional
from uuid import UUID

import psycopg
from psycopg.rows import dict_row

from states.state import State

from .query_builders import _build_load_linked_film_ids_query, _build_load_updated_ids_query


class AbstractUpdatesWatcher(abc.ABC):
    table_name = None
    time_stamp_key = None
    id_key = None

    def __init__(self, conn: psycopg.Connection, state: State):
        self._conn = conn
        self._state = state

        if None in [self.table_name, self.time_stamp_key, self.id_key]:
            raise NotImplementedError("Please provide either table_name, time_stamp_key and id_key.")

    def _update_state(self, last_timestamp, last_id) -> None:
        self._state.set_state_bulk({self.time_stamp_key: last_timestamp, self.id_key: last_id}, uncommitted=True)

    def get_films_for_update(self) -> list[UUID]:
        prev_processed_timestamp = self._state.get_state(self.time_stamp_key)
        prev_processed_id = self._state.get_state(self.id_key)

        uncommitted_timestamp = self._state.get_state(State.uncommitted_prefix + self.time_stamp_key)
        uncommitted_id = self._state.get_state(State.uncommitted_prefix + self.id_key)

        ids, latest_timestamp, latest_id = self._load_updated_ids(
            self.table_name, prev_processed_timestamp, prev_processed_id, uncommitted_timestamp, uncommitted_id
        )

        if not ids:
            return []

        self._update_state(latest_timestamp, latest_id)
        film_ids = self._get_linked_film_ids(ids)
        return film_ids

    def _load_updated_ids(
        self,
        table_name: str,
        prev_processed_timestamp: Optional[datetime] = None,
        prev_processed_id: Optional[str] = None,
        uncommitted_timestamp: Optional[datetime] = None,
        uncommitted_id: Optional[str] = None,
    ) -> tuple[list[UUID], datetime | None, UUID | None]:
        query = _build_load_updated_ids_query(
            table_name, prev_processed_timestamp, prev_processed_id, uncommitted_timestamp, uncommitted_id
        )
        with self._conn.cursor(row_factory=dict_row) as cur:
            cur.execute(query)
            results = cur.fetchone()

        ids = results["ids"] if results["ids"] is not None else []
        latest_timestamp = results["latest_timestamp"]
        latest_id = ids[-1] if ids else None

        return ids, latest_timestamp, latest_id

    def _get_linked_film_ids(self, ids: list[UUID]) -> list[UUID]:
        query = _build_load_linked_film_ids_query(self.table_name, len(ids))
        with self._conn.cursor() as cur:
            cur.execute(query, ids)
            results = cur.fetchall()
        results = [i[0] for i in results]
        return results


class PersonUpdatesWatcher(AbstractUpdatesWatcher):
    table_name = "person"
    time_stamp_key = "last_processed_person_timestamp"
    id_key = "last_processed_person_id"


class GenreUpdatesWatcher(AbstractUpdatesWatcher):
    table_name = "genre"
    time_stamp_key = "last_processed_genre_timestamp"
    id_key = "last_processed_genre_id"


class FilmWorkUpdatesWatcher(AbstractUpdatesWatcher):
    table_name = "film_work"
    time_stamp_key = "last_processed_film_work_timestamp"
    id_key = "last_processed_film_work_id"

    def _get_linked_film_ids(self, ids: list[UUID]) -> list[UUID]:
        return ids
