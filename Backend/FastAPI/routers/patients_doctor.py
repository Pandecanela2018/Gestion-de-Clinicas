from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from db.client import db_client
from db.schemas.Doctor import doctor_schema
from db.schemas.patient import patients_schema
from utils.session import get_session
from bson import ObjectId
from datetime import datetime

templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix="/doctor")

@router.get("/patients", response_class=HTMLResponse)
async def patients_doctor(request: Request):
    session = get_session(request)
    
    if not session or "doctor_id" not in session:
        return RedirectResponse(url="/login-doctor", status_code=302)
    
    doctor_id = session["doctor_id"]
    
    try:
        doctor = db_client.Prueba.Doctor.find_one({"_id": ObjectId(doctor_id)})
        doctor_data = doctor_schema(doctor)
        
        doctor_full_name = f"{doctor_data['name']} {doctor_data['surname']}"
        
        # Obtener pacientes registrados por este doctor
        patients = list(db_client.Prueba.Patient.find({"doctor_name": doctor_full_name}))
        
        return templates.TemplateResponse("patients.html", {
            "request": request,
            "doctor": doctor_data,
            "patients": patients
        })
    except Exception as e:
        print(f"Error: {e}")
        return RedirectResponse(url="/login-doctor", status_code=302)


@router.get("/register-patient", response_class=HTMLResponse)
async def register_patient_page(request: Request):
    session = get_session(request)
    
    if not session or "doctor_id" not in session:
        return RedirectResponse(url="/login-doctor", status_code=302)
    
    doctor_id = session["doctor_id"]
    
    try:
        doctor = db_client.Prueba.Doctor.find_one({"_id": ObjectId(doctor_id)})
        doctor_data = doctor_schema(doctor)
        
        return templates.TemplateResponse("register_patient.html", {
            "request": request,
            "doctor": doctor_data
        })
    except Exception as e:
        print(f"Error: {e}")
        return RedirectResponse(url="/login-doctor", status_code=302)


@router.post("/register-patient", response_class=HTMLResponse)
async def register_patient_post(
    request: Request,
    name: str = Form(...),
    surname: str = Form(...),
    dui: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    birth_date: str = Form(...),
    file_number: int = Form(...)
):
    session = get_session(request)
    
    if not session or "doctor_id" not in session:
        return RedirectResponse(url="/login-doctor", status_code=302)
    
    doctor_id = session["doctor_id"]
    
    try:
        doctor = db_client.Prueba.Doctor.find_one({"_id": ObjectId(doctor_id)})
        doctor_data = doctor_schema(doctor)
        doctor_full_name = f"{doctor_data['name']} {doctor_data['surname']}"
        
        # Convertir birth_date string a datetime
        birth_date_obj = datetime.strptime(birth_date, "%Y-%m-%d")
        
        # Crear nuevo paciente
        new_patient = {
            "name": name,
            "surname": surname,
            "dui": dui,
            "email": email,
            "phone": int(phone),
            "birth_date": birth_date_obj,
            "file_number": file_number,
            "doctor_name": doctor_full_name
        }
        
        result = db_client.Prueba.Patient.insert_one(new_patient)
        
        return RedirectResponse(url="/doctor/patients", status_code=302)
    except Exception as e:
        print(f"Error: {e}")
        return RedirectResponse(url="/login-doctor", status_code=302)


@router.get("/doctor/patients", response_class=HTMLResponse)
async def get_patients_list(request: Request):
    # Obtener el doctor de la sesión o token
    doctor = request.session.get("doctor")  # Ajusta según tu autenticación
    
    if not doctor:
        return {"error": "No autenticado"}
    
    # Obtener todos los pacientes de la BD
    patients_data = list(db_client.Prueba.Patient.find())
    patients = patients_schema(patients_data)
    
    return templates.TemplateResponse("patients.html", {
        "request": request,
        "doctor": doctor,
        "patients": patients
    })