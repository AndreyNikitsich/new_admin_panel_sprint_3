import logging

import backoff
from elasticsearch import ConnectionError, ConnectionTimeout, Elasticsearch, helpers
from pydantic import BaseModel

from settings import settings

logger = logging.getLogger(__name__)


class ElasticLoader:
    def __init__(self, client: Elasticsearch, index_name: str):
        self._client = client
        self._index_name = index_name

    @backoff.on_exception(
        backoff.expo, (ConnectionError, ConnectionTimeout), max_time=settings.others.elastic_backoff_max_time
    )
    def load(self, data: list[BaseModel]):
        actions = (
            {
                "_index": self._index_name,
                "_id": i.id,
                "_source": i.model_dump(by_alias=True),
            }
            for i in data
        )
        result = helpers.bulk(self._client, actions)
        logger.debug("Rows was loaded to Elasticsearch: %s", result[0])
