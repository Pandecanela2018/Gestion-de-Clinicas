from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from db.client import db_client
from db.schemas.patient import patient_schema
from bson import ObjectId
from utils.session import get_session

templates = Jinja2Templates(directory="templates")
router = APIRouter()


@router.get('/expedientes/{patient_id}', response_class=HTMLResponse)
async def expediente_page(patient_id: str, request: Request):
    """Render the medical record (expediente) for a patient."""
    session = get_session(request)
    if not session or 'doctor_id' not in session:
        return RedirectResponse(url="/login-doctor", status_code=302)

    try:
        patient = db_client.Prueba.Patient.find_one({'_id': ObjectId(patient_id)})
        if not patient:
            return RedirectResponse(url="/doctor/patients", status_code=302)

        patient_data = patient_schema(patient)

        # Load consultations for this patient
        consultations_cursor = db_client.Prueba.Consultation.find({'patient_id': patient.get('_id')}).sort('created_at', -1)
        consultations = []
        for c in consultations_cursor:
            consultations.append({
                'id': str(c.get('_id')),
                'created_at': c.get('created_at'),
                'historia': c.get('historia', {}),
                'exploracion': c.get('exploracion', {}),
                'diagnostico': c.get('diagnostico', {}),
                'laboratorio': c.get('laboratorio', {}),
                'recetas': c.get('recetas', {}),
                'seguimiento': c.get('seguimiento', {})
            })

        # Load appointments for this patient (best-effort by name)
        name_parts = patient.get('name', '').split()
        appointments = []
        if name_parts:
            appointments_cursor = db_client.Prueba.Appointment.find({'patient_name': {'$regex': name_parts[0], '$options': 'i'}}).sort('date', -1)
            for a in appointments_cursor:
                appointments.append({
                    'id': str(a.get('_id')),
                    'date': a.get('date'),
                    'time': a.get('time'),
                    'status': a.get('status'),
                    'notes': a.get('notes')
                })

        return templates.TemplateResponse('expedientes.html', {
            'request': request,
            'patient': patient_data,
            'consultations': consultations,
            'appointments': appointments
        })
    except Exception as e:
        print('Error rendering expediente:', e)
        return RedirectResponse(url="/doctor/patients", status_code=302)
