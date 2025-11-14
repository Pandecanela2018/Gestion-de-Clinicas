from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from db.client import db_client
from db.schemas.Doctor import doctor_schema
from utils.session import get_session
from bson import ObjectId
from datetime import datetime, date, timedelta

templates = Jinja2Templates(directory="templates")
router = APIRouter()

@router.get("/dashboard-doctor", response_class=HTMLResponse)
async def dashboard_doctor(request: Request):
    session = get_session(request)
    
    if not session or "doctor_id" not in session:
        return RedirectResponse(url="/login-doctor", status_code=302)
    
    doctor_id = session["doctor_id"]
    
    try:
        doctor = db_client.Prueba.Doctor.find_one({"_id": ObjectId(doctor_id)})
        doctor_data = doctor_schema(doctor)
        
        # Obtener nombre completo del doctor
        doctor_full_name = f"{doctor_data['name']} {doctor_data['surname']}"
        
        # Filtro para hoy
        today = date.today()
        start_of_day = datetime.combine(today, datetime.min.time())
        end_of_day = datetime.combine(today, datetime.max.time())
        
        # Total de pacientes registrados en el sistema
        total_patients = db_client.Prueba.Patient.count_documents({})
        
        # Citas de hoy
        today_appointments = db_client.Prueba.Appointment.count_documents({
            "doctor_name": doctor_full_name,
            "date": {"$gte": start_of_day, "$lte": end_of_day}
        })
        
        # Consultas activas: citas confirmadas del doctor
        active_consultations = db_client.Prueba.Appointment.count_documents({
            "doctor_name": doctor_full_name,
            "status": "confirmed"
        })
        
        recent_patients = list(db_client.Prueba.Patient.find().limit(5))
        
        appointments_today = list(db_client.Prueba.Appointment.find({
            "doctor_name": doctor_full_name,
            "date": {"$gte": start_of_day, "$lte": end_of_day}
        }).limit(5))
        
        return templates.TemplateResponse("dashboard-doctor.html", {
            "request": request,
            "doctor": doctor_data,
            "total_patients": total_patients,
            "today_appointments": today_appointments,
            "active_consultations": active_consultations,
            "recent_patients": recent_patients,
            "appointments_today": appointments_today
        })
    except Exception as e:
        print(f"Error: {e}")
        return RedirectResponse(url="/login-doctor", status_code=302)