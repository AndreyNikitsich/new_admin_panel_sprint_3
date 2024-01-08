from uuid import UUID

from pydantic import BaseModel, Field


class Person(BaseModel):
    id: UUID
    name: str


class Film(BaseModel):
    id: UUID = Field(validation_alias="film_id")
    imdb_rating: float | None
    title: str
    description: str

    genre: list[str]

    director: list[str]
    actors_names: list[str]
    writers_names: list[str]

    actors: list[Person]
    writers: list[Person]
