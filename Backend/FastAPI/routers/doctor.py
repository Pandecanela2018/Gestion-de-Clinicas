from fastapi import APIRouter, HTTPException, status
from db.models.Doctor import Doctor
from db.client import db_client
from db.schemas.Doctor import doctor_schema

router = APIRouter()

router = APIRouter(prefix="/doctor",
                   tags=["doctor"],
                   responses={404: {"message": "No encontrado"}})



@router.post("/", response_model=Doctor, status_code=status.HTTP_201_CREATED)
async def doctor(doctor: Doctor):

    doctor_dict = dict(doctor)
    del doctor_dict["id"]
    del doctor_dict["Horario_ID_Ref"]

    id = db_client.Prueba.Doctor.insert_one(doctor_dict).inserted_id

    new_doctor = doctor_schema(db_client.Prueba.Doctor.find_one({"_id":id}))

    return Doctor(**new_doctor)