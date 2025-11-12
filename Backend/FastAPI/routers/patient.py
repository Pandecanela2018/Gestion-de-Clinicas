from fastapi import APIRouter, HTTPException, status, Form
from fastapi.responses import RedirectResponse
from db.models.patient import Patient, PatientP
from db.schemas.patient import patient_schema, patients_schema
from utils.security import hash_password, verify_password
from db.client import db_client
from bson import ObjectId
from datetime import datetime

router = APIRouter()

router = APIRouter(prefix="/patient",
                   tags=["patient"],
                   responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}})


@router.get("/", response_model=list[Patient])
async def patients():
    return patients_schema(db_client.Prueba.Patient.find())

@router.get("/{id}")
async def get_patient(id: str):
    return search_patient("_id", ObjectId(id))

@router.post("/", response_model=Patient, status_code=status.HTTP_201_CREATED)
async def create_patient(patient: PatientP):
    if type(search_patient("email", patient.email)) == Patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="El usuario ya existe"
        )

    patient_dict = dict(patient)
    if patient.password:
        patient_dict["password"] = hash_password(patient_dict["password"])
    del patient_dict["id"]

    id = db_client.Prueba.Patient.insert_one(patient_dict).inserted_id

    new_patient = patient_schema(db_client.Prueba.Patient.find_one({"_id": id}))

    return Patient(**new_patient)

@router.put("/", response_model=Patient)
async def update_patient(patient: PatientP):
    patient_dict = dict(patient)
    del patient_dict["id"]

    if patient.password:
        patient_dict["password"] = hash_password(patient.password)
    else:
        del patient_dict["password"]

    try:
        db_client.Prueba.Patient.find_one_and_replace({"_id": ObjectId(patient.id)}, patient_dict)
    except:
        return {"error": "No se ha actualizado el usuario"}
    
    return search_patient("_id", ObjectId(patient.id))

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(id: str):
    found = db_client.Prueba.Patient.find_one_and_delete({"_id": ObjectId(id)})

    if not found:
        return {"error": "No se ha eliminado el usuario"}

def search_patient(field: str, key):
    try:
        patient = db_client.Prueba.Patient.find_one({field: key})
        return Patient(**patient_schema(patient))
    except:
        return {"error": "No se ha encontrado el usuario"}

@router.post("/register", status_code=status.HTTP_303_SEE_OTHER)
async def register_patient(
    name: str = Form(...),
    surname: str = Form(...),
    second_surname: str | None = Form(None),
    dui: str = Form(...),
    email: str | None = Form(None),
    phone: str = Form(...),
    birth_date: str = Form(...),
    file_number: int = Form(...),
    gender: str = Form(...),
    address: str = Form(...),
    city: str = Form(...),
    province: str = Form(...),
    postal_code: str | None = Form(None),
    blood_type: str = Form(...),
    allergies: str | None = Form(None),
    chronic_diseases: str | None = Form(None),
    medications: str | None = Form(None),
    emergency_name: str = Form(...),
    emergency_phone: str = Form(...),
    emergency_relation: str = Form(...),
    has_insurance_raw: str | None = Form(None),
    password: str | None = Form(None)
):
    # convertir fecha (HTML date => datetime para MongoDB)
    try:
        birth_date_parsed = datetime.strptime(birth_date, "%Y-%m-%d")
    except Exception:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")

    has_insurance = True if has_insurance_raw is not None else False

    patient_data = {
        "name": name,
        "surname": surname,
        "second_surname": second_surname,
        "dui": dui,
        "email": email,
        "phone": phone,
        "birth_date": birth_date_parsed,
        "file_number": file_number,
        "gender": gender,
        "address": address,
        "city": city,
        "province": province,
        "postal_code": postal_code,
        "blood_type": blood_type,
        "allergies": allergies,
        "chronic_diseases": chronic_diseases,
        "medications": medications,
        "emergency_name": emergency_name,
        "emergency_phone": emergency_phone,
        "emergency_relation": emergency_relation,
        "has_insurance": has_insurance
    }

    if password:
        patient_data["password"] = hash_password(password)

    db_client.Prueba.Patient.insert_one(patient_data)

    # Redirige a la página de pacientes registrados
    return RedirectResponse(url="/doctor/patients", status_code=status.HTTP_303_SEE_OTHER)

