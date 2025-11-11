from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from utils.session import get_session
from db.client import db_client
from bson import ObjectId
from db.schemas.patient import patient_schema
from db.schemas.diagnostic import diagnostic_schema
import logging

#Esta viculado supuestamente a diagnostico por ahora, eso debe verse y cambiarse


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

templates = Jinja2Templates(directory="templates")

router = APIRouter()


@router.get("/receta")
def receta(request: Request):
    session = get_session(request)
    if not session:
        return RedirectResponse(url="/login", status_code=302)

    try:
        patient_doc = db_client.Prueba.Patient.find_one({"_id": ObjectId(session.get("user_id"))})
    except Exception:
        logger.exception("Error buscando paciente para recetas: %s", session.get("user_id"))
        return RedirectResponse(url="/login", status_code=302)

    if not patient_doc:
        return RedirectResponse(url="/login", status_code=302)

    patient = patient_schema(patient_doc)
    # Buscar diagnósticos/recetas por folio médico
    medical_record = patient.get('file_number')
    # Build a flexible query to match numeric or string-stored medical_record values
    candidates = [medical_record, str(medical_record)]
    try:
        mr_int = int(medical_record)
        if mr_int not in candidates:
            candidates.append(mr_int)
    except Exception:
        pass

    diag_cursor = db_client.Prueba.Diagnostic.find({"medical_record": {"$in": candidates}}).sort("date", -1)

    # Normalize documents for template (format date to readable string)
    diagnostics = []
    from datetime import datetime
    for d in diag_cursor:
        diag = diagnostic_schema(d)
        dt = diag.get('date')
        try:
            if isinstance(dt, datetime):
                diag['date'] = dt.strftime('%Y-%m-%d %H:%M')
            else:
                # leave as string if not a datetime
                diag['date'] = str(dt)
        except Exception:
            diag['date'] = str(dt)
        diagnostics.append(diag)

    return templates.TemplateResponse("recetas.html", {"request": request, "patient": patient, "diagnostics": diagnostics})
