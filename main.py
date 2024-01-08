import time

import psycopg
from elasticsearch import Elasticsearch

from etl.extract.extractor import Extractor
from etl.load.elastic_loader import ElasticLoader
from etl.transform.transformer import Transformer
from settings import settings
from states.state import State
from storages.json_file_storage import JsonFileStorage

if __name__ == "__main__":
    with psycopg.connect(**settings.postgres.model_dump()) as conn:
        file_storage = JsonFileStorage()
        state = State(file_storage)
        extractor = Extractor.get_object(conn, state)

        transformer = Transformer()

        es = Elasticsearch(settings.elastic.url)
        loader = ElasticLoader(es, settings.elastic.index_name)

        count = 1
        while True:
            i = 0
            for batch in extractor.extract_films_batch():
                print("Batch number: ", i)
                transformed_batch = transformer.transform(batch)
                loader.load(transformed_batch)
                i+=1
            state.commit_state()
            print("Loaded")
            count += 1
            time.sleep(settings.others.etl_sleep_seconds)
