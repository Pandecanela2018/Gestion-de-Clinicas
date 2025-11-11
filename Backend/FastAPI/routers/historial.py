from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from utils.session import get_session
from db.client import db_client
from bson import ObjectId
from db.schemas.patient import patient_schema
from db.schemas.Appointment import appointments_schema
from db.schemas.diagnostic import diagnostic_schema
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

templates = Jinja2Templates(directory="templates")

router = APIRouter()


@router.get("/historial")
def historial(request: Request):
    session = get_session(request)
    if not session:
        return RedirectResponse(url="/login", status_code=302)

    try:
        patient_doc = db_client.Prueba.Patient.find_one({"_id": ObjectId(session.get("user_id"))})
    except Exception:
        logger.exception("Error buscando paciente para historial: %s", session.get("user_id"))
        return RedirectResponse(url="/login", status_code=302)

    if not patient_doc:
        return RedirectResponse(url="/login", status_code=302)

    patient = patient_schema(patient_doc)

    # Citas: intentar varias búsquedas como en dashboard
    full_name = f"{patient_doc.get('name')} {patient_doc.get('surname')}"
    appointments_docs = list(db_client.Prueba.Appointment.find({"patient_name": full_name}))
    if not appointments_docs:
        appointments_docs = list(db_client.Prueba.Appointment.find({"patient_dui": patient_doc.get('dui')}))
    if not appointments_docs:
        appointments_docs = list(db_client.Prueba.Appointment.find({"patient_name": {"$regex": patient_doc.get('name', ''), "$options": "i"}}))

    appointments = appointments_schema(appointments_docs)

    # Diagnósticos / Recetas: buscar por file_number (medical_record)
    medical_record = patient.get('file_number')
    candidates = [medical_record, str(medical_record)]
    try:
        mr_int = int(medical_record)
        if mr_int not in candidates:
            candidates.append(mr_int)
    except Exception:
        pass

    diag_cursor = db_client.Prueba.Diagnostic.find({"medical_record": {"$in": candidates}}).sort("date", -1)
    diagnostics = []
    for d in diag_cursor:
        diag = diagnostic_schema(d)
        dt = diag.get('date')
        try:
            if isinstance(dt, datetime):
                diag['date'] = dt.strftime('%Y-%m-%d %H:%M')
            else:
                diag['date'] = str(dt)
        except Exception:
            diag['date'] = str(dt)
        diagnostics.append(diag)

    # Placeholder arrays for medications/allergies/vaccines (not modelled yet)
    medications = []
    allergies = []
    vaccines = []

    return templates.TemplateResponse("historial_medico.html", {"request": request, "patient": patient, "appointments": appointments, "diagnostics": diagnostics, "medications": medications, "allergies": allergies, "vaccines": vaccines})
