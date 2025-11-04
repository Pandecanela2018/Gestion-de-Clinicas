from fastapi import APIRouter, HTTPException, status
from db.models.Appointment import Appointment
from db.schemas.Appointment import appointment_schema, appointments_schema
from db.client import db_client
from bson import ObjectId

router = APIRouter()

router = APIRouter(prefix="/appointment",
                   tags=["appointment"],
                   responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}})

@router.get("/", response_model=list[Appointment])
async def appointments():
    return appointments_schema(db_client.Prueba.Appointment.find())

@router.get("/{id}")
async def appointment(id: str):
    return search_appointment("_id", ObjectId(id))

@router.get("/")
async def appointment(id: str):
    return search_appointment("_id", ObjectId(id))

@router.post("/", response_model=Appointment, status_code=status.HTTP_201_CREATED)
async def appointment(appointment: Appointment):
    existing_appointment = db_client.Prueba.Appointment.find_one({
        "doctor_name": appointment.doctor_name,
        "date": appointment.date
    })
    
    if existing_appointment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una cita para este doctor en este día"
        )

    appointment_dict = dict(appointment)
    del appointment_dict["id"]

    id = db_client.Prueba.Appointment.insert_one(appointment_dict).inserted_id

    new_appointment = appointment_schema(db_client.Prueba.Appointment.find_one({"_id": id}))

    return Appointment(**new_appointment)

@router.put("/", response_model=Appointment)
async def appointment(appointment: Appointment):

    appointment_dict = dict(appointment)
    del appointment_dict["id"]

    try:
        db_client.Prueba.Appointment.find_one_and_replace({"_id": ObjectId(appointment.id)}, appointment_dict)
    except:
        return {"error": "No se ha actualizado la cita"}
    
    return search_appointment("_id", ObjectId(appointment.id))


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def appointment(id: str):
    found = db_client.Prueba.Appointment.find_one_and_delete({"_id": ObjectId(id)})

    if not found:
        return {"error": "No se ha eliminado la cita"}

def search_appointment(field: str, key):
    try:
        appointment = db_client.Prueba.Appointment.find_one({field: key})
        return Appointment(**appointment_schema(appointment))
    except:
        return{"error": "No se ha encontrado la cita"}
    
# prueba1