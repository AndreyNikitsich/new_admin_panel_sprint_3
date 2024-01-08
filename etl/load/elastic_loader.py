from elasticsearch import Elasticsearch, helpers
from pydantic import BaseModel


class ElasticLoader:
    def __init__(self, client: Elasticsearch, index_name: str):
        self._client = client
        self._index_name = index_name

    def load(self, data: list[BaseModel]):
        actions = (
            {
                "_index": self._index_name,
                "_id": i.id,
                "_source": i.model_dump(by_alias=True),
            }
            for i in data
        )
        helpers.bulk(self._client, actions)
