import abc
from psycopg.connection import Connection
from states.state import State

class BaseTableWatcher(abc.ABC):
    
    state_key = None
    
    def __init__(self, connection: Connection, state: State) -> None:
        self._connection = connection
        self._state = state
        
        if self.state_key is None:
            raise NotImplemented()
    
    @abc.abstractmethod
    def get_query():
        raise NotImplemented()
    
    def get_film_ids(self):
        with self._connection.cursor() as cur:
            cur.execute(self.get_query())
            ids = cur.fetchall()
            
        return ids
            