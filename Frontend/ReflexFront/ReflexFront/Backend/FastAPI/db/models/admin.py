from pydantic import BaseModel
from typing import Optional

class Admin(BaseModel):
    id: Optional[str] = None
    name: str
    surname: str
    email: str
    username: str

class AdminP(BaseModel):
    id: Optional[str] = None
    name: str
    surname: str
    email: str
    username: str
    password: Optional[str] = None