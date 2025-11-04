from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class Appointment(BaseModel):
    id: Optional[str] = None
    patient_name: str
    doctor_name: str
    date: datetime
    status: str