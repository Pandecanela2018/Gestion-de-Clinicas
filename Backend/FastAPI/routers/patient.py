from fastapi import APIRouter, HTTPException, status
from db.models.patient import Patient
from db.schemas.patient import patient_schema, patients_schema
from db.client import db_client
from bson import ObjectId

router = APIRouter()

router = APIRouter(prefix="/patient",
                   tags=["patient"],
                   responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}})


@router.get("/", response_model=list[Patient])
async def patients():
    return patients_schema(db_client.Prueba.Patient.find())

@router.get("/{id}")
async def doctor(id: str):
    return search_patient("_id", ObjectId(id))

@router.get("/")
async def doctor(id: str):
    return search_patient("_id", ObjectId(id))

@router.post("/", response_model=Patient, status_code=status.HTTP_201_CREATED)
async def patient(patient: Patient):
    if type(search_patient("email", patient.email)) == Patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="El usuario ya existe"
        )
    
    patient_dict = dict(patient)
    del patient_dict["id"]

    id = db_client.Prueba.Patient.insert_one(patient_dict).inserted_id

    new_patient = patient_schema(db_client.Prueba.Patient.find_one({"_id": id}))

    return Patient(**new_patient)

@router.put("/", response_model=Patient)
async def patient(patient: Patient):

    patient_dict = dict(patient)
    del patient_dict["id"]

    try:
        db_client.Prueba.Patient.find_one_and_replace({"_id": ObjectId(patient.id)}, patient_dict)
    except:
        return {"error": "No se ha actualizado el usuario"}
    
    return search_patient("_id", ObjectId(patient.id))

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def patient(id: str):
    found = db_client.Prueba.Patient.find_one_and_delete({"_id": ObjectId(id)})

    if not found:
        return {"error": "No se a eliminado el usuario"}

def search_patient(field: str, key):
    try:
        patient = db_client.Prueba.Patient.find_one({field: key})
        return Patient(**patient_schema(patient))
    except:
        return{"error": "No se ha encontrado el usuario"}