from fastapi import APIRouter, HTTPException, status
from db.models.Doctor import Doctor, DoctorP
from db.schemas.Doctor import doctor_schema, doctors_schema
from utils.security import hash_password, verify_password
from db.client import db_client
from bson import ObjectId

router = APIRouter()

router = APIRouter(prefix="/doctor",
                   tags=["doctor"],
                   responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}})

@router.get("/", response_model=list[Doctor])
async def doctors():
    return doctors_schema(db_client.Prueba.Doctor.find())

@router.get("/{id}") #Path
async def doctor(id: str):
    return search_doctor("_id", ObjectId(id))

@router.get("/") #Query
async def doctor(id: str):
    return search_doctor("_id", ObjectId(id))

@router.post("/", response_model=Doctor, status_code=status.HTTP_201_CREATED)
async def doctor(doctor: DoctorP):
    if type(search_doctor("email", doctor.email)) == Doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="El usuario ya existe"
        )

    doctor_dict = dict(doctor)
    doctor_dict["password"] = hash_password(doctor_dict["password"])
    del doctor_dict["id"]

    id = db_client.Prueba.Doctor.insert_one(doctor_dict).inserted_id

    new_doctor = doctor_schema(db_client.Prueba.Doctor.find_one({"_id": id}))

    return Doctor(**new_doctor)

@router.put("/", response_model=Doctor)
async def doctor(doctor: DoctorP):

    doctor_dict = dict(doctor)
    del doctor_dict["id"]

    if doctor.password:
        doctor_dict["password"] = hash_password(doctor.password)
    else:
        del doctor_dict["password"]

    try:
        db_client.Prueba.Doctor.find_one_and_replace({"_id": ObjectId(doctor.id)}, doctor_dict)
    except:
        return {"error": "No se a actualizado el usuario"}
    
    return search_doctor("_id", ObjectId(doctor.id))


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def doctor(id: str):
    found = db_client.Prueba.Doctor.find_one_and_delete({"_id": ObjectId(id)})

    if not found:
        return {"error": "No se a eliminado el usuario"}

def search_doctor(field: str, key):
    try:
        doctor = db_client.Prueba.Doctor.find_one({field: key})
        return Doctor(**doctor_schema(doctor))
    except:
        return{"error": "No se ha encontrado el usuario"}