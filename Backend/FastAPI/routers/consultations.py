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

        # Try to get patient id from appointment (preferred) or fallback to name search
        patient_id = None
        if appointment.get('patient_id'):
            try:
                patient_id = ObjectId(appointment.get('patient_id'))
            except Exception:
                patient_id = appointment.get('patient_id')
        elif appointment.get('patient_name'):
            patient_doc = db_client.Prueba.Patient.find_one({'name': {'$regex': appointment.get('patient_name').strip().split()[0], '$options': 'i'}})
            if patient_doc:
                patient_id = patient_doc.get('_id')

        # Determine per-patient autoincremented consultation number
        consulta_number = None
        if patient_id:
            try:
                # Count documents matching either ObjectId or string form to handle inconsistent storage
                query = {'$or': [{'patient_id': patient_id}, {'patient_id': str(patient_id)}]}
                current_count = db_client.Prueba.Consultation.count_documents(query)
                consulta_number = int(current_count) + 1
            except Exception:
                consulta_number = 1

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

        # Attach consulta number if available
        if consulta_number is not None:
            consultation_doc['consulta_number'] = consulta_number

        res = db_client.Prueba.Consultation.insert_one(consultation_doc)

        # If we have a patient id, append medicamentos/antecedentes to the Patient document
        if patient_id:
            try:
                # Normalize any existing non-list fields into arrays so $push works
                existing_patient = db_client.Prueba.Patient.find_one({'_id': patient_id})
                if existing_patient:
                    # Convert medications to list if it's a single string or dict
                    if 'medications' in existing_patient and not isinstance(existing_patient.get('medications'), list):
                        db_client.Prueba.Patient.update_one({'_id': patient_id}, {'$set': {'medications': [existing_patient.get('medications')]}})
                    if 'chronic_diseases' in existing_patient and not isinstance(existing_patient.get('chronic_diseases'), list):
                        db_client.Prueba.Patient.update_one({'_id': patient_id}, {'$set': {'chronic_diseases': [existing_patient.get('chronic_diseases')]}})
                    if 'allergies' in existing_patient and not isinstance(existing_patient.get('allergies'), list):
                        db_client.Prueba.Patient.update_one({'_id': patient_id}, {'$set': {'allergies': [existing_patient.get('allergies')]}})

                # Handle recetas -> medications
                meds = payload.get('recetas')
                meds_list = []
                if meds:
                    if isinstance(meds, list):
                        meds_list = meds
                    elif isinstance(meds, dict):
                        # try common keys inside recetas
                        for k in ('medicamentos', 'meds', 'prescriptions'):
                            if meds.get(k):
                                if isinstance(meds.get(k), list):
                                    meds_list = meds.get(k)
                                else:
                                    meds_list = [meds.get(k)]
                                break
                        if not meds_list:
                            # if dict but no known keys, push the dict as-is
                            meds_list = [meds]
                    else:
                        meds_list = [meds]

                # Handle chronic diseases
                chronic = payload.get('chronic_diseases') or payload.get('enfermedadesCronicas') or payload.get('cronicas')
                chronic_list = []
                if chronic:
                    if isinstance(chronic, list):
                        chronic_list = chronic
                    else:
                        chronic_list = [chronic]

                # Handle allergies
                allergies = payload.get('allergies') or payload.get('alergias')
                allergies_list = []
                if allergies:
                    if isinstance(allergies, list):
                        allergies_list = allergies
                    else:
                        allergies_list = [allergies]

                push_obj = {}
                if meds_list:
                    push_obj['medications'] = {'$each': meds_list}
                if chronic_list:
                    push_obj['chronic_diseases'] = {'$each': chronic_list}
                if allergies_list:
                    push_obj['allergies'] = {'$each': allergies_list}

                if push_obj:
                    # Log what we will push for easier debugging
                    print('Updating Patient', patient_id, 'with push:', push_obj)
                    db_client.Prueba.Patient.update_one({'_id': patient_id}, {'$push': push_obj}, upsert=False)
            except Exception as e:
                print('Warning: failed to update patient with new antecedentes/meds', e)

        # Mark appointment as completed
        db_client.Prueba.Appointment.update_one({'_id': ObjectId(appointment_id)}, {'$set': {'status': 'completed'}})

        return JSONResponse({'ok': True, 'consultation_id': str(res.inserted_id), 'consulta_number': consulta_number})
    except Exception as e:
        print('Error saving consultation:', e)
        import traceback
        traceback.print_exc()
        return JSONResponse({'error': 'internal error'}, status_code=500)
