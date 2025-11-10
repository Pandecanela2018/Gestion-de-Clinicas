from fastapi import APIRouter, Request, status
from fastapi.responses import RedirectResponse
from utils.session import get_session
from db.client import db_client
from fastapi.templating import Jinja2Templates
from bson import ObjectId
from db.schemas.patient import patient_schema
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

templates = Jinja2Templates(directory="templates")

router = APIRouter()


@router.get("/calendario")
def calendario(request: Request):
    """Muestra la página de calendario con todas las citas programadas."""
    session = get_session(request)
    logger.debug("/calendario called. session=%s", session)
    if not session:
        return RedirectResponse(url="/login", status_code=302)

    # Buscar paciente por id de sesión
    try:
        patient_doc = db_client.Prueba.Patient.find_one({"_id": ObjectId(session.get("user_id"))})
        logger.debug("patient_doc fetched: %s", {k: patient_doc.get(k) for k in ['_id','name','surname','dui']} if patient_doc else None)
    except Exception:
        logger.exception("Error buscando paciente por user_id: %s", session.get("user_id"))
        return RedirectResponse(url="/login", status_code=302)

    if not patient_doc:
        return RedirectResponse(url="/login", status_code=302)

    patient = patient_schema(patient_doc)

    return templates.TemplateResponse("calendario_user.html", {"request": request, "patient": patient})


@router.get("/appointments/")
def get_appointments(request: Request):
    """Retorna las citas del paciente autenticado en formato JSON."""
    session = get_session(request)
    if not session:
        return RedirectResponse(url="/login", status_code=302)

    try:
        patient_doc = db_client.Prueba.Patient.find_one({"_id": ObjectId(session.get("user_id"))})
        if not patient_doc:
            return []

        patient_name = patient_doc.get("name", "")
        
        # Buscar todas las citas del paciente
        appointments = db_client.Prueba.Appointment.find({"patient_name": patient_name})
        
        result = []
        for appointment in appointments:
            # Convertir date datetime a formato YYYY-MM-DD para el calendario
            date_obj = appointment.get("date")
            if isinstance(date_obj, str):
                date_str = date_obj.split("T")[0]
            else:
                date_str = date_obj.strftime("%Y-%m-%d") if date_obj else ""
            
            result.append({
                "id": str(appointment["_id"]),
                "patient_name": appointment.get("patient_name", ""),
                "doctor_name": appointment.get("doctor_name", ""),
                "day": date_str,
                "date": str(appointment.get("date", "")),
                "status": appointment.get("status", "scheduled")
            })
        
        return result
    except Exception as e:
        logger.exception("Error al obtener citas: %s", e)
        return []
