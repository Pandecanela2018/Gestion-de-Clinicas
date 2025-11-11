from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from utils.session import get_session
from db.client import db_client
from bson import ObjectId
from db.schemas.patient import patient_schema
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

templates = Jinja2Templates(directory="templates")

router = APIRouter()


@router.get("/agendar")
def agendar(request: Request):
    """Muestra el formulario para agendar una cita."""
    session = get_session(request)
    logger.debug("/agendar called. session=%s", session)
    if not session:
        return RedirectResponse(url="/login", status_code=302)

    try:
        patient_doc = db_client.Prueba.Patient.find_one({"_id": ObjectId(session.get("user_id"))})
    except Exception:
        logger.exception("Error buscando paciente por user_id: %s", session.get("user_id"))
        return RedirectResponse(url="/login", status_code=302)

    if not patient_doc:
        return RedirectResponse(url="/login", status_code=302)

    patient = patient_schema(patient_doc)
    return templates.TemplateResponse("agendar_cita.html", {"request": request, "patient": patient})
