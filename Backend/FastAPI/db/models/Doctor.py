from pydantic import BaseModel
from typing import Optional

class Doctor(BaseModel):
    id: Optional[str] = None
    name: str
    surname: str
    speciality: str
    email: str
    phone: int
    dui: str

class DoctorP(BaseModel):
    id: Optional[str] = None
    name: str
    surname: str
    speciality: str
    email: str
    phone: int
    dui: str
    password: Optional[str] = None