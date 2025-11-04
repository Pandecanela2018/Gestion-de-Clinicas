from fastapi import APIRouter, HTTPException, status
from db.models.Schedule import Schedule
from db.schemas.Schedule import schedule_schema, schedules_schema
from db.client import db_client
from bson import ObjectId

router = APIRouter()

router = APIRouter(prefix="/schedule",
                   tags=["schedule"],
                   responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}})


@router.get("/", response_model=list[Schedule])
async def schedules():
    return schedules_schema(db_client.Prueba.Schedule.find())

@router.get("/{id}")
async def schedule(id: str):
    return search_schedule("_id", ObjectId(id))

@router.get("/")
async def schedule(id: str):
    return search_schedule("_id", ObjectId(id))

@router.post("/", response_model=Schedule, status_code=status.HTTP_201_CREATED)
async def schedule(schedule: Schedule):
    existing_schedule = db_client.Prueba.Schedule.find_one({
        "doctor_name": schedule.doctor_name,
        "day": schedule.day
    })
    
    if existing_schedule:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un horario para este doctor en este día"
        )

    schedule_dict = dict(schedule)
    del schedule_dict["id"]

    id = db_client.Prueba.Schedule.insert_one(schedule_dict).inserted_id

    new_schedule = schedule_schema(db_client.Prueba.Schedule.find_one({"_id": id}))

    return Schedule(**new_schedule)

@router.put("/", response_model=Schedule)
async def schedule(schedule: Schedule):

    schedule_dict = dict(schedule)
    del schedule_dict["id"]

    try:
        db_client.Prueba.Schedule.find_one_and_replace({"_id": ObjectId(schedule.id)}, schedule_dict)
    except:
        return {"error": "No se ha actualizado el horario"}
    
    return search_schedule("_id", ObjectId(schedule.id))

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def schedule(id: str):
    found = db_client.Prueba.Schedule.find_one_and_delete({"_id": ObjectId(id)})

    if not found:
        return {"error": "No se ha eliminado el horario"}

def search_schedule(field: str, key):
    try:
        schedule = db_client.Prueba.Schedule.find_one({field: key})
        return Schedule(**schedule_schema(schedule))
    except:
        return{"error": "No se ha encontrado el horario"}
    
#prueba1