from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from db.client import db_client
from db.schemas.Doctor import doctor_schema
from bson import ObjectId

templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix="/doctor")

@router.get("/patients", response_class=HTMLResponse)
async def patients_doctor(request: Request):
    doctor_id = request.cookies.get("doctor_id")
    
    if not doctor_id:
        return RedirectResponse(url="/login-doctor", status_code=302)
    
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