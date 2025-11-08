from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class File(BaseModel):
    id: Optional[str] = None
    file_number: int
    creation_date: datetime
    observation_general: str