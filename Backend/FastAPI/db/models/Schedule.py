from pydantic import BaseModel
from typing import Optional


class Schedule(BaseModel):
    id: Optional[str] = None
    doctor_name: str
    day: str
    hour_start: str
    hour_end: str