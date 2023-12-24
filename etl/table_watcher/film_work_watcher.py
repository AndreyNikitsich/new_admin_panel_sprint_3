from .base import BaseTableWatcher


class FilmWorkWatcher(BaseTableWatcher):
    state_key = "film_work_latest"
    
    def get_query(self):
        return "SELECT id, modified FROM film_work LIMIT 10000;"
    