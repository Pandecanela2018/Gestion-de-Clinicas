from fastapi import APIRouter, HTTPException, status
from db.models.doctor import Doctor
from db.schemas.doctor import doctor_schema, doctors_schema
from db.client import db_client
from bson import ObjectId

router = APIRouter()

router = APIRouter(prefix="/doctor",
                   tags=["doctor"],
                   responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}})

@router.get("/", response_model=list[Doctor])
async def doctors():
    return doctors_schema(db_client.Prueba.Doctor.find())

@router.get("/{id}")
async def doctor(id: str):
    return search_doctor("_id", ObjectId(id))

@router.get("/")
async def doctor(id: str):
    return search_doctor("_id", ObjectId(id))

@router.post("/", response_model=Doctor, status_code=status.HTTP_201_CREATED)
async def doctor(doctor: Doctor):
    if type(search_doctor("email", doctor.email)) == Doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="El usuario ya existe"
        )

    doctor_dict = dict(doctor)
    del doctor_dict["id"]

    id = db_client.Prueba.Doctor.insert_one(doctor_dict).inserted_id

    new_doctor = doctor_schema(db_client.Prueba.Doctor.find_one({"_id": id}))

    return Doctor(**new_doctor)

@router.put("/", response_model=Doctor)
async def doctor(doctor: Doctor):

    doctor_dict = dict(doctor)
    del doctor_dict["id"]

    try:
        db_client.Prueba.Doctor.find_one_and_replace({"_id": ObjectId(doctor.id)}, doctor_dict)
    except:
        return {"error": "No se a actualziado el usuario"}
    
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