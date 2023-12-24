from typing import LiteralString
from uuid import UUID
from models import ModifiedEntry, EntryId
from states.state import State
from storages.json_file_storage import JsonFileStorage
from settings import db_settings
import psycopg
from psycopg import sql
from psycopg.rows import dict_row, class_row
import datetime

SETTINGS = db_settings()

def _get_modified_rows(conn: psycopg.Connection, state: State, state_key: str, table_name: str, row_class=ModifiedEntry):
    query_template = "SELECT {fields} FROM {table_name} WHERE modified > %s"
    latest = state.get_state(state_key)
    if latest is not None:
        latest = datetime.datetime.fromisoformat(latest)
    else:
        latest = datetime.datetime.min
    query = sql.SQL(query_template).format(
        fields=sql.SQL(", ").join([sql.Identifier(i) for i in row_class.model_fields.keys()]),
        table_name=sql.Identifier(table_name),
    )
    with conn.cursor(row_factory=class_row(row_class)) as cur:
        cur.execute(query, (latest,))
        data = cur.fetchall()
    return data


def get_modified_persons(conn: psycopg.Connection, state: State):
    state_key = "person_latest"
    table_name = "person"
    data = _get_modified_rows(conn, state, state_key, table_name)
    return data

def get_modified_genres(conn: psycopg.Connection, state: State):
    state_key = "genres_latest"
    table_name = "genre"
    data = _get_modified_rows(conn, state, state_key, table_name)
    return data

def _get_film_ids_for_modified_entry(query_template: LiteralString, entries: list[ModifiedEntry]) -> list[EntryId]:
    query = sql.SQL(query_template).format(
        entry_ids=sql.SQL(", ").join([sql.Literal(i.id) for i in entries])
    )
    with conn.cursor() as cur:
        cur.execute(query)
        data = cur.fetchall()
    return data


def get_film_ids_for_persons(entries: list[ModifiedEntry]) -> list[EntryId]:
    query_template = """
        SELECT fw.id, pfw.person_id FROM film_work fw
        LEFT JOIN person_film_work pfw ON fw.id=pfw.film_work_id
        WHERE pfw.person_id IN ({entry_ids})
    """
    return _get_film_ids_for_modified_entry(query_template, entries)


def get_film_ids_for_genres(entries: list[ModifiedEntry]) -> list[EntryId]:
    query_template = """
        SELECT DISTINCT fw.id FROM film_work fw
        LEFT JOIN genre_film_work gfw ON fw.id=gfw.film_work_id
        WHERE gfw.genre_id IN ({entry_ids})
    """
    return _get_film_ids_for_modified_entry(query_template, entries)    


def get_films_by_ids(conn: psycopg.Connection, ids: list[str]):
    query = sql.SQL(
        """
            SELECT
                fw.id AS fw_id, 
                fw.title, 
                fw.description, 
                fw.rating, 
                fw.type, 
                fw.created, 
                fw.modified, 
                pfw.role, 
                person.id, 
                person.full_name,
                genre.name AS genre
            FROM film_work fw
            LEFT JOIN person_film_work pfw ON fw.id = pfw.film_work_id
            LEFT JOIN person ON pfw.person_id = person.id
            LEFT JOIN genre_film_work gfw ON fw.id = gfw.film_work_id
            LEFT JOIN genre ON gfw.genre_id = genre.id
            WHERE fw.id IN ({})
        """).format(
            sql.SQL(", ").join(sql.Literal(i) for i in ids)
    )
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query)
        data = cur.fetchall()
    return data
    


if __name__ == "__main__":
    file_storage = JsonFileStorage()
    state = State(file_storage)

    with psycopg.connect(**SETTINGS.model_dump()) as conn:
        modified_persons = get_modified_persons(conn, state)
        modified_genres = get_modified_genres(conn, state)
        
        film_ids_from_persons = get_film_ids_for_persons(modified_persons)
        film_ids_from_genres = get_film_ids_for_genres(modified_genres)
        
        
        
        # films_from_persons = get_films_by_ids(conn, modified_persons)
        
        
        
        print("Modified persons: ", len(modified_persons))
        print("Modified genres: ", len(modified_genres))
        print("Films from persons: ", len(film_ids_from_persons))
        print("Films from genres: ", len(film_ids_from_genres))



