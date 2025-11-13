from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from db.client import db_client
from db.schemas.patient import patient_schema
from bson import ObjectId
from utils.session import get_session

templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix="/expedientes",
                   tags=["expedientes"])


@router.get('/', response_class=HTMLResponse)
async def expedientes_list(request: Request):
    """Display all medical records (expedientes) for all patients."""
    session = get_session(request)
    if not session or 'doctor_id' not in session:
        return RedirectResponse(url="/login-doctor", status_code=302)

    try:
        doctor_id = session['doctor_id']
        doctor = db_client.Prueba.Doctor.find_one({'_id': ObjectId(doctor_id)})
        
        # Get all patients
        patients_data = list(db_client.Prueba.Patient.find())
        patients = []
        
        for patient in patients_data:
            patient_info = patient_schema(patient)
            # Count consultations for each patient
            consultations_count = db_client.Prueba.Consultation.count_documents({'patient_id': patient.get('_id')})
            patient_info['consultations_count'] = consultations_count
            patients.append(patient_info)
        
        return templates.TemplateResponse('expedientes_list.html', {
            'request': request,
            'doctor': doctor,
            'patients': patients
        })
    except Exception as e:
        print('Error rendering expedientes list:', e)
        import traceback
        traceback.print_exc()
        return RedirectResponse(url="/login-doctor", status_code=302)


@router.get('/{patient_id}', response_class=HTMLResponse)
async def expediente_page(patient_id: str, request: Request):
    """Render the medical record (expediente) for a patient."""
    session = get_session(request)
    if not session or 'doctor_id' not in session:
        return RedirectResponse(url="/login-doctor", status_code=302)

    try:
        print(f"DEBUG: Buscando paciente con ID: {patient_id}")
        
        # Intentar convertir a ObjectId
        try:
            patient_oid = ObjectId(patient_id)
            print(f"DEBUG: ObjectId válido: {patient_oid}")
        except Exception as e:
            print(f"DEBUG: Error convirtiendo a ObjectId: {e}")
            return RedirectResponse(url="/expedientes", status_code=302)
        
        patient = db_client.Prueba.Patient.find_one({'_id': patient_oid})
        print(f"DEBUG: Paciente encontrado: {patient is not None}")
        
        if not patient:
            print(f"DEBUG: Paciente no encontrado en BD")
            return RedirectResponse(url="/expedientes", status_code=302)

        patient_data = patient_schema(patient)
        print(f"DEBUG: Datos del paciente: {patient_data}")

        # Get doctor info for sidebar
        doctor_id = session['doctor_id']
        doctor = db_client.Prueba.Doctor.find_one({'_id': ObjectId(doctor_id)})
        doctor_data = {"name": "Doctor", "surname": "Sistema", "speciality": "Médico"}
        if doctor:
            from db.schemas.Doctor import doctor_schema
            doctor_data = doctor_schema(doctor)

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

        print(f"DEBUG: Renderizando expedientes.html para paciente: {patient_data.get('name')}")
        print(f"DEBUG: Consultations: {len(consultations)}, Appointments: {len(appointments)}")
        
        return templates.TemplateResponse('expedientes.html', {
            'request': request,
            'patient': patient_data,
            'consultations': consultations,
            'appointments': appointments,
            'doctor': doctor_data
        })
    except Exception as e:
        print(f'Error rendering expediente: {e}')
        import traceback
        traceback.print_exc()
        return RedirectResponse(url="/expedientes", status_code=302)
