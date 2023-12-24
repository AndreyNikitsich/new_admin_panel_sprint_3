from datetime import datetime
from typing import List
from uuid import UUID
from pydantic import BaseModel

class ModifiedEntry(BaseModel):
    id: UUID
    modified: datetime

class EntryId(BaseModel):
    id: UUID
