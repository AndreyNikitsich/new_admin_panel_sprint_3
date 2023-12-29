from uuid import UUID

import psycopg

from extract.film_ids import get_film_ids_for_genres, get_film_ids_for_persons

from extract.film_work import get_films_by_ids
from extract.modified_entries import get_modified_genres, get_modified_persons
from settings import db_settings
from states.state import State
from storages.json_file_storage import JsonFileStorage

SETTINGS = db_settings()

def get_films(film_ids: list[UUID], batch_size: int = 100):
    batch = []
    for index, _id in enumerate(film_ids, 1):
        batch.append(_id)
        if index % batch_size == 0 or index == len(film_ids):
            yield _id, get_films_by_ids(conn, batch)
            batch.clear()


if __name__ == "__main__":
    file_storage = JsonFileStorage()
    state = State(file_storage)

    with psycopg.connect(**SETTINGS.model_dump()) as conn:
        modified_persons = get_modified_persons(conn, state)
        modified_persons_ids = [i.id for i in modified_persons]

        last_film_id = state.get_state("from_person_latest_film_id")
        films_from_persons = get_film_ids_for_persons(conn, modified_persons_ids, last_film_id=last_film_id)
        film_ids_from_persons = [i.film_id for i in films_from_persons]

        batch_number = 1
        for _id, raw_films_batch in get_films(film_ids_from_persons):
            try:
                print("Batch number: ", batch_number)
                print(f"Run extract for batch size: {len(raw_films_batch)}")
                print(f"Load for batch size: {len(raw_films_batch)}")
                state.set_state("from_person_latest_film_id", str(film_ids_from_persons[-1]))
                state.set_state("person_latest", str(film_ids_from_persons[-1]))
            except BaseException as e:
                state.set_state("from_person_latest_film_id", str(_id))
            batch_number += 1



