from pydantic import BaseModel

class Doctor(BaseModel):
    id: str | None
    name: str
    surname: str
    Horario_ID_Ref: None
    speciality: str
    email: str
    cellphone: int 