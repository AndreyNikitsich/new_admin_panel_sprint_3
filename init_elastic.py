import json

from elasticsearch import BadRequestError, Elasticsearch

from settings import settings

resource_already_exists_msg = "resource_already_exists_exception"

if __name__ == "__main__":
    with open(settings.elastic.index_file_name) as f:
        index_config = json.load(f)
    client = Elasticsearch(settings.elastic.url)
    try:
        client.indices.create(
            index=settings.elastic.index_name, settings=index_config["settings"], mappings=index_config["mappings"]
        )
    except BadRequestError as e:
        if e.message != resource_already_exists_msg:
            raise e
