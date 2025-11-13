from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from db.client import db_client
from db.schemas.Doctor import doctor_schema
from bson import ObjectId
from datetime import datetime
from utils.session import get_session

templates = Jinja2Templates(directory="templates")
router = APIRouter()

@router.get('/consultations', response_class=HTMLResponse)
async def consultations_page(request: Request):
    """Render consultations page"""
    session = get_session(request)
    
    if not session or 'doctor_id' not in session:
        return RedirectResponse(url="/login-doctor", status_code=302)
    
    doctor_id = session['doctor_id']
    
    try:
        doctor = db_client.Prueba.Doctor.find_one({'_id': ObjectId(doctor_id)})
        doctor_data = doctor_schema(doctor)
        
        return templates.TemplateResponse("consultas.html", {
            "request": request,
            "doctor": doctor_data
        })
    except Exception as e:
        print(f"Error: {e}")
        return RedirectResponse(url="/login-doctor", status_code=302)


@router.post('/consultations/{appointment_id}/save')
async def save_consultation(appointment_id: str, request: Request):
    """Save consultation data for an appointment into Consultation collection and mark appointment completed"""
    session = get_session(request)
    if not session or 'doctor_id' not in session:
        return JSONResponse({'error': 'Not authenticated'}, status_code=401)

    try:
        payload = await request.json()

        # Find appointment
        appointment = db_client.Prueba.Appointment.find_one({'_id': ObjectId(appointment_id)})
        if not appointment:
            return JSONResponse({'error': 'Appointment not found'}, status_code=404)

        # Try to get patient id if appointment contains patient identifier
        patient_id = None
        if appointment.get('patient_name'):
            patient_doc = db_client.Prueba.Patient.find_one({'name': {'$regex': appointment.get('patient_name').split()[0], '$options': 'i'}})
            if patient_doc:
                patient_id = patient_doc.get('_id')

        consultation_doc = {
            'appointment_id': ObjectId(appointment_id),
            'patient_id': patient_id,
            'doctor_id': ObjectId(session['doctor_id']) if session.get('doctor_id') else None,
            'created_at': datetime.utcnow(),
            'historia': payload.get('historia', {}),
            'exploracion': payload.get('exploracion', {}),
            'diagnostico': payload.get('diagnostico', {}),
            'laboratorio': payload.get('laboratorio', {}),
            'recetas': payload.get('recetas', {}),
            'seguimiento': payload.get('seguimiento', {})
        }

        res = db_client.Prueba.Consultation.insert_one(consultation_doc)

        # Mark appointment as completed
        db_client.Prueba.Appointment.update_one({'_id': ObjectId(appointment_id)}, {'$set': {'status': 'completed'}})

        return JSONResponse({'ok': True, 'consultation_id': str(res.inserted_id)})
    except Exception as e:
        print('Error saving consultation:', e)
        import traceback
        traceback.print_exc()
        return JSONResponse({'error': 'internal error'}, status_code=500)
