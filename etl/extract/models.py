import datetime
from uuid import UUID

from pydantic import BaseModel


class FilmRow(BaseModel):
    film_id: UUID
    title: str
    description: str
    rating: float | None
    type: str
    created: datetime.datetime | None
    modified: datetime.datetime | None

    person_id: UUID | None
    person_name: str | None
    person_role: str | None

    genre_id: UUID | None
    genre_name: str | None


Batch = list[FilmRow]
