from collections import defaultdict
from typing import Generator

from etl.extract.models import Batch

from .models import Film


class Transformer:
    def transform(self, rows: Batch) -> list[Film]:
        result = []
        for film_rows in self._group_rows_by_film_id(rows):
            film_info = self._merge_film_rows(film_rows)
            result.append(film_info)
        return result

    @staticmethod
    def _group_rows_by_film_id(data: Batch) -> Generator[Batch, None, None]:
        film_info = []
        prev_id = data[0].film_id
        rows_count = len(data)
        for i in range(rows_count):
            row = data[i]
            if row.film_id != prev_id:
                yield film_info
                film_info.clear()
            film_info.append(row)
            prev_id = row.film_id
        yield film_info

    @staticmethod
    def _merge_film_rows(film_rows: Batch) -> Film:
        base_info = film_rows[0].model_dump()
        base_info["imdb_rating"] = base_info["rating"]

        unique_persons_grouped_by_role = defaultdict(set)
        for row in film_rows:
            if row.person_role is not None:
                unique_persons_grouped_by_role[row.person_role].add((row.person_id, row.person_name))

        genres = {row.genre_name for row in film_rows if row.genre_name}

        persons_grouped_by_role = {
            k: [{"id": i[0], "name": i[1]} for i in v] for k, v in unique_persons_grouped_by_role.items()
        }

        merged_info = {
            "genre": genres,
            "writers": persons_grouped_by_role.get("writer", []),
            "actors": persons_grouped_by_role.get("actor", []),
            "director": [i["name"] for i in persons_grouped_by_role.get("director", [])],
            "writers_names": [i["name"] for i in persons_grouped_by_role.get("writer", [])],
            "actors_names": [i["name"] for i in persons_grouped_by_role.get("actor", [])],
        }

        init_dict = {**base_info, **merged_info}
        return Film.model_validate(init_dict)
