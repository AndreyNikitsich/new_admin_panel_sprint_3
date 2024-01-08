from datetime import datetime
from typing import Optional

from psycopg import sql


def _build_load_updated_ids_query(
    table_name: str,
    prev_processed_timestamp: Optional[datetime] = None,
    prev_processed_id: Optional[str] = None,
    uncommitted_timestamp: Optional[datetime] = None,
    uncommitted_id: Optional[str] = None,
):
    query_template = sql.SQL(
        """
            SELECT
              max(t.modified) as latest_timestamp,
              array_agg(t.id ORDER BY t.modified ASC, t.id ASC) as ids
            FROM {table_name} t
            {where_clause}
        """
    )
    where_clause = _build_load_updated_ids_query_where_clause(
        prev_processed_timestamp, prev_processed_id, uncommitted_timestamp, uncommitted_id
    )
    query = query_template.format(where_clause=where_clause, table_name=sql.Identifier(table_name))
    return query


def _build_load_updated_ids_query_where_clause(
    prev_processed_timestamp: Optional[datetime] = None,
    prev_processed_id: Optional[str] = None,
    uncommitted_timestamp: Optional[datetime] = None,
    uncommitted_id: Optional[str] = None,
):
    where_clause = sql.SQL("")
    if None not in [prev_processed_timestamp, prev_processed_id]:
        where_clause = sql.SQL(
            """
                WHERE
                (
                  (
                    t.modified = {prev_processed_timestamp}
                    AND t.id > {prev_processed_genre_id}
                  )
                  OR t.modified > {prev_processed_timestamp}
                )
            """
        ).format(
            prev_processed_timestamp=sql.Literal(prev_processed_timestamp),
            prev_processed_genre_id=sql.Literal(prev_processed_id),
        )

    if None not in [prev_processed_timestamp, prev_processed_id, uncommitted_timestamp, uncommitted_id]:
        where_clause = sql.SQL(
            """
                WHERE
                (
                  (
                    t.modified = {prev_processed_timestamp}
                    AND t.modified <= {uncommitted_timestamp}
                    AND t.id > {prev_processed_genre_id}
                    AND t.id <= {uncommitted_id}
                  )
                  OR t.modified > {prev_processed_timestamp}
                )
            """
        ).format(
            prev_processed_timestamp=sql.Literal(prev_processed_timestamp),
            prev_processed_genre_id=sql.Literal(prev_processed_id),
            uncommitted_timestamp=sql.Literal(prev_processed_timestamp),
            uncommitted_id=sql.Literal(prev_processed_id),
        )
    return where_clause


def _build_load_linked_film_ids_query(table_name: str, ids_count: int):
    query = sql.SQL("""SELECT DISTINCT film_work_id FROM {m2m_table} WHERE {id_column} in ({values})""").format(
        m2m_table=sql.Identifier(f"{table_name}_film_work"),
        id_column=sql.Identifier(f"{table_name}_id"),
        values=sql.SQL(", ").join(sql.Placeholder() for _ in range(ids_count)),
    )
    return query


def _build_load_film_info_query(ids_count: int):
    query = sql.SQL(
        """
        SELECT
            fw.id AS film_id,
            fw.title,
            fw.description,
            fw.rating,
            fw.type,
            fw.created,
            fw.modified,
            person.id AS person_id,
            person.full_name as person_name,
            pfw.role as person_role,
            genre.id AS genre_id,
            genre.name AS genre_name
        FROM film_work fw
        LEFT JOIN person_film_work pfw ON fw.id = pfw.film_work_id
        LEFT JOIN person ON pfw.person_id = person.id
        LEFT JOIN genre_film_work gfw ON fw.id = gfw.film_work_id
        LEFT JOIN genre ON gfw.genre_id = genre.id
        WHERE fw.id IN ({ids})
        ORDER BY fw.id
    """
    ).format(ids=sql.SQL(", ").join(sql.Placeholder() for _ in range(ids_count)))
    return query
