import logging
import time

from etl.extract.extractor import Extractor
from etl.load.elastic_loader import ElasticLoader
from etl.transform.transformer import Transformer
from settings import settings
from states.state import State
from storages.json_file_storage import JsonFileStorage

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    file_storage = JsonFileStorage()
    state = State(file_storage)

    extractor = Extractor.get_object(state)
    transformer = Transformer()
    loader = ElasticLoader.get_object()

    logger.info("ETL worker started. Waiting for updates...")
    while True:
        updated_films_count = 0
        for i, batch in enumerate(extractor.extract_films_batch(), 1):
            if i == 1:
                logger.info("Changes in Postgres were detected. Start ETL process")

            logger.info("Processing batch №%s", i)
            transformed_batch = transformer.transform(batch)
            loader.load(transformed_batch)
            updated_films_count += len(transformed_batch)

        if updated_films_count != 0:
            logger.info(
                "Changes processed successfully. %s films were updated in Elasticsearch. Waiting for updates...",
                updated_films_count,
            )
            state.commit_state()

        time.sleep(settings.others.etl_sleep_seconds)
