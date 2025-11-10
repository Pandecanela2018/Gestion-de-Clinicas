from fastapi import APIRouter, Request, status
from fastapi.responses import RedirectResponse
from utils.session import get_session
from db.client import db_client
from fastapi.templating import Jinja2Templates
from bson import ObjectId
from db.schemas.patient import patient_schema
from db.schemas.Appointment import appointments_schema
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

templates = Jinja2Templates(directory="templates")

# Usaremos la ruta directa /dashboard para coincidir con el redirect después del login
router = APIRouter()


@router.get("/dashboard")
def dashboard(request: Request):
    """Muestra la página principal del usuario logeado con info básica y próximas citas."""
    session = get_session(request)
    logger.debug("/dashboard called. session=%s", session)
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

    # Buscar citas asociadas al paciente. Intentamos varias coincidencias para mayor robustez.
    full_name = f"{patient_doc.get('name')} {patient_doc.get('surname')}"

    # Ejecutar varias búsquedas y tomar la primera que devuelva resultados.
    # Ejecutar varias búsquedas y tomar la primera que devuelva resultados.
    appointments_docs = list(db_client.Prueba.Appointment.find({"patient_name": full_name}))
    logger.debug("Search by full_name '%s' returned %d docs", full_name, len(appointments_docs))

    if not appointments_docs:
        appointments_docs = list(db_client.Prueba.Appointment.find({"patient_dui": patient_doc.get('dui')}))
        logger.debug("Search by patient_dui '%s' returned %d docs", patient_doc.get('dui'), len(appointments_docs))

    if not appointments_docs:
        # búsqueda por nombre parcial (regex, case-insensitive)
        appointments_docs = list(db_client.Prueba.Appointment.find({"patient_name": {"$regex": patient_doc.get('name', ''), "$options": "i"}}))
        logger.debug("Search by name regex '%s' returned %d docs", patient_doc.get('name', ''), len(appointments_docs))

    logger.debug("Total appointments_docs to process: %d", len(appointments_docs))

    appointments = appointments_schema(appointments_docs)

    # Filtrar próximas citas (fecha >= ahora) y ordenar por fecha ascendente
    now = datetime.now()
    upcoming = [a for a in appointments if (isinstance(a.get('date'), datetime) and a.get('date') >= now) or (not isinstance(a.get('date'), datetime))]
    upcoming.sort(key=lambda x: x.get('date') if isinstance(x.get('date'), datetime) else datetime.max)

    # Pasar solo unas pocas citas para la vista principal
    upcoming_preview = upcoming[:5]

    logger.debug("Upcoming preview length: %d", len(upcoming_preview))
    return templates.TemplateResponse("dashboard_user.html", {"request": request, "patient": patient, "appointments": upcoming_preview})