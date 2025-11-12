from pydantic import BaseModel
from typing import Optional
from datetime import date

class Patient(BaseModel):
    id: Optional[str] = None
    name: str
    surname: str
    second_surname: Optional[str] = None
    dui: str
    email: Optional[str] = None
    phone: str
    birth_date: date
    file_number: int
    gender: str
    address: str
    city: str
    province: str
    postal_code: Optional[str] = None
    blood_type: str
    allergies: Optional[str] = None
    chronic_diseases: Optional[str] = None
    medications: Optional[str] = None
    emergency_name: str
    emergency_phone: str
    emergency_relation: str
    has_insurance: Optional[bool] = False

class PatientP(BaseModel):
    id: Optional[str] = None
    name: str
    surname: str
    second_surname: Optional[str] = None
    dui: str
    email: Optional[str] = None
    phone: str
    birth_date: date
    file_number: int
    gender: str
    address: str
    city: str
    province: str
    postal_code: Optional[str] = None
    blood_type: str
    allergies: Optional[str] = None
    chronic_diseases: Optional[str] = None
    medications: Optional[str] = None
    emergency_name: str
    emergency_phone: str
    emergency_relation: str
    has_insurance: Optional[bool] = False
    password: Optional[str] = None

