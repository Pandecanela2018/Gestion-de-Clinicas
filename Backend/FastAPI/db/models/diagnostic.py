from pydantic import BaseModel
from typing import Optional
from datetime import  datetime

class Diagnostic(BaseModel):
    id: Optional[str] = None
    medical_record : int
    date : datetime
    description : str
    treatment : str