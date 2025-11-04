from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class Patient(BaseModel):
    id: Optional[str] = None
    name: str
    surname: str
    dui: str
    email: str
    phone: int
    birth_date: datetime

    file_number: int

class PatientP(BaseModel):
    id: Optional[str] = None
    name: str
    surname: str
    dui: str
    email: str
    phone: int
    birth_date: datetime
    file_number: int
    password: Optional[str] = None

