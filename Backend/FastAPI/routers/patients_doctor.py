from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from db.client import db_client
from db.schemas.Doctor import doctor_schema
from db.schemas.patient import patients_schema
from utils.session import get_session
from bson import ObjectId
from datetime import datetime

templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix="/doctor")

@router.get("/patients", response_class=HTMLResponse)
async def patients_doctor(request: Request):
    session = get_session(request)
    
    if not session or "doctor_id" not in session:
        return RedirectResponse(url="/login-doctor", status_code=302)
    
    doctor_id = session["doctor_id"]
    
    try:
        doctor = db_client.Prueba.Doctor.find_one({"_id": ObjectId(doctor_id)})
        doctor_data = doctor_schema(doctor)
        
        # Obtener TODOS los pacientes de la base de datos
        patients_data = list(db_client.Prueba.Patient.find())
        patients = patients_schema(patients_data)
        
        print(f"Pacientes encontrados: {len(patients)}")
        for p in patients:
            print(f"  - {p['name']} {p['surname']}")
        
        return templates.TemplateResponse("patients.html", {
            "request": request,
            "doctor": doctor_data,
            "patients": patients
        })
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return RedirectResponse(url="/login-doctor", status_code=302)


@router.get("/register-patient", response_class=HTMLResponse)
async def register_patient_page(request: Request):
    session = get_session(request)
    
    if not session or "doctor_id" not in session:
        return RedirectResponse(url="/login-doctor", status_code=302)
    
    doctor_id = session["doctor_id"]
    
    try:
        doctor = db_client.Prueba.Doctor.find_one({"_id": ObjectId(doctor_id)})
        doctor_data = doctor_schema(doctor)
        
        return templates.TemplateResponse("register_patient.html", {
            "request": request,
            "doctor": doctor_data
        })
    except Exception as e:
        print(f"Error: {e}")
        return RedirectResponse(url="/login-doctor", status_code=302)


@router.post("/register-patient", response_class=HTMLResponse)
async def register_patient_post(
    request: Request,
    name: str = Form(...),
    surname: str = Form(...),
    second_surname: str = Form(None),
    dui: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    birth_date: str = Form(...),
    file_number: int = Form(...),
    gender: str = Form(...),
    address: str = Form(...),
    city: str = Form(...),
    province: str = Form(...),
    postal_code: str = Form(None),
    blood_type: str = Form(...),
    allergies: str = Form(None),
    chronic_diseases: str = Form(None),
    medications: str = Form(None),
    emergency_name: str = Form(...),
    emergency_phone: str = Form(...),
    emergency_relation: str = Form(...),
    has_insurance_raw: str = Form(None),
    password: str = Form(None)
):
    session = get_session(request)
    
    if not session or "doctor_id" not in session:
        return RedirectResponse(url="/login-doctor", status_code=302)
    
    doctor_id = session["doctor_id"]
    
    try:
        doctor = db_client.Prueba.Doctor.find_one({"_id": ObjectId(doctor_id)})
        doctor_data = doctor_schema(doctor)
        doctor_full_name = f"{doctor_data['name']} {doctor_data['surname']}"
        
        # Convertir birth_date string a datetime
        birth_date_obj = datetime.strptime(birth_date, "%Y-%m-%d")
        has_insurance = True if has_insurance_raw is not None else False
        
        # Crear nuevo paciente
        new_patient = {
            "name": name,
            "surname": surname,
            "second_surname": second_surname,
            "dui": dui,
            "email": email,
            "phone": phone,
            "birth_date": birth_date_obj,
            "file_number": file_number,
            "gender": gender,
            "address": address,
            "city": city,
            "province": province,
            "postal_code": postal_code,
            "blood_type": blood_type,
            "allergies": allergies,
            "chronic_diseases": chronic_diseases,
            "medications": medications,
            "emergency_name": emergency_name,
            "emergency_phone": emergency_phone,
            "emergency_relation": emergency_relation,
            "has_insurance": has_insurance,
            "doctor_name": doctor_full_name
        }
        
        result = db_client.Prueba.Patient.insert_one(new_patient)
        print(f"Paciente registrado: {result.inserted_id}")
        
        return RedirectResponse(url="/doctor/patients", status_code=302)
    except Exception as e:
        print(f"Error al registrar paciente: {e}")
        return RedirectResponse(url="/login-doctor", status_code=302)


# --- New endpoints to manage appointments pending/confirm/cancel ---


@router.get('/appointments/pending')
async def get_pending_appointments(request: Request):
    session = get_session(request)
    if not session:
        return JSONResponse({'error': 'Not authenticated'}, status_code=401)

    try:
        # Get doctor identity from session
        doctor_id = session.get('doctor_id') or (session.get('doctor') and session.get('doctor').get('id'))
        doctor_doc = None
        doctor_full_name = None

        if doctor_id:
            try:
                doctor_doc = db_client.Prueba.Doctor.find_one({'_id': ObjectId(doctor_id)})
            except Exception:
                doctor_doc = db_client.Prueba.Doctor.find_one({'_id': doctor_id})

        if doctor_doc:
            doctor_full_name = f"{doctor_doc.get('name','')} {doctor_doc.get('surname','')}"
            print(f"Doctor full name: {doctor_full_name}")

        # Build query to match scheduled appointments (status: "scheduled")
        # Match by doctor_name (case-insensitive)
        if doctor_full_name and doctor_full_name.strip():
            query = {
                'status': 'scheduled',
                'doctor_name': {'$regex': f"^{doctor_full_name}$", '$options': 'i'}
            }
        else:
            # If no doctor found, show all scheduled appointments
            query = {'status': 'scheduled'}

        pending = list(db_client.Prueba.Appointment.find(query))

        # Serialize minimal fields for frontend
        out = []
        for a in pending:
            out.append({
                'id': str(a.get('_id')),
                'patient_name': a.get('patient_name', 'N/A'),
                'time': a.get('time', ''),
                'date': a.get('date').isoformat() if isinstance(a.get('date'), datetime) else (a.get('date') or ''),
                'reason': a.get('reason', ''),
                'status': a.get('status', '')
            })

        print(f"Pending appointments found: {len(out)}")
        return JSONResponse(out)
    except Exception as e:
        print('Error fetching pending appointments:', e)
        import traceback
        traceback.print_exc()
        return JSONResponse({'error': 'internal error'}, status_code=500)


@router.post('/appointments/{appointment_id}/confirm')
async def confirm_appointment(appointment_id: str, request: Request):
    session = get_session(request)
    if not session or 'doctor_id' not in session:
        return JSONResponse({'error': 'Not authenticated'}, status_code=401)

    try:
        res = db_client.Prueba.Appointment.update_one({'_id': ObjectId(appointment_id)}, {'$set': {'status': 'confirmed'}})
        if res.modified_count:
            return JSONResponse({'ok': True})
        return JSONResponse({'ok': False, 'message': 'No update performed'}, status_code=404)
    except Exception as e:
        print('Error confirming appointment:', e)
        return JSONResponse({'error': 'internal error'}, status_code=500)


@router.post('/appointments/{appointment_id}/cancel')
async def cancel_appointment(appointment_id: str, request: Request):
    session = get_session(request)
    if not session or 'doctor_id' not in session:
        return JSONResponse({'error': 'Not authenticated'}, status_code=401)

    try:
        res = db_client.Prueba.Appointment.update_one({'_id': ObjectId(appointment_id)}, {'$set': {'status': 'cancelled'}})
        if res.modified_count:
            return JSONResponse({'ok': True})
        return JSONResponse({'ok': False, 'message': 'No update performed'}, status_code=404)
    except Exception as e:
        print('Error cancelling appointment:', e)
        return JSONResponse({'error': 'internal error'}, status_code=500)


# DEBUG ENDPOINT - Remove after testing
@router.get('/debug/appointments-sample')
async def debug_appointments_sample(request: Request):
    try:
        # List all collections in the database
        db = db_client.Prueba
        collections = db.list_collection_names()
        
        result = {
            'all_collections': collections,
            'appointment_collections': [c for c in collections if 'appointment' in c.lower()],
        }
        
        # Try multiple possible collection names
        for col_name in ['Appointment', 'appointment', 'Appointments', 'appointments']:
            try:
                count = db[col_name].count_documents({})
                result[f'{col_name}_count'] = count
                
                if count > 0:
                    sample = list(db[col_name].find().limit(5))
                    out = []
                    for a in sample:
                        a['_id'] = str(a['_id'])
                        for key, val in list(a.items()):
                            if isinstance(val, datetime):
                                a[key] = val.isoformat()
                        out.append(a)
                    result[f'{col_name}_sample'] = out
            except Exception as e:
                result[f'{col_name}_error'] = str(e)
        
        print(f"Debug info: {result}")
        return JSONResponse(result)
    except Exception as e:
        print('Error in debug endpoint:', e)
        import traceback
        traceback.print_exc()
        return JSONResponse({'error': str(e)}, status_code=500)


# Endpoints for confirmed appointments and consultation details
@router.get('/appointments/confirmed')
async def get_confirmed_appointments(request: Request):
    """Get list of confirmed appointments for the logged-in doctor"""
    session = get_session(request)
    if not session:
        return JSONResponse({'error': 'Not authenticated'}, status_code=401)

    try:
        doctor_id = session.get('doctor_id')
        doctor_doc = None
        doctor_full_name = None

        if doctor_id:
            try:
                doctor_doc = db_client.Prueba.Doctor.find_one({'_id': ObjectId(doctor_id)})
            except Exception:
                doctor_doc = db_client.Prueba.Doctor.find_one({'_id': doctor_id})

        if doctor_doc:
            doctor_full_name = f"{doctor_doc.get('name','')} {doctor_doc.get('surname','')}"

        # Build query for confirmed appointments
        if doctor_full_name and doctor_full_name.strip():
            query = {
                'status': 'confirmed',
                'doctor_name': {'$regex': f"^{doctor_full_name}$", '$options': 'i'}
            }
        else:
            query = {'status': 'confirmed'}

        confirmed = list(db_client.Prueba.Appointment.find(query))

        out = []
        for a in confirmed:
            out.append({
                'id': str(a.get('_id')),
                'patient_name': a.get('patient_name', 'N/A'),
                'time': a.get('time', ''),
                'date': a.get('date').isoformat() if isinstance(a.get('date'), datetime) else (a.get('date') or ''),
                'reason': a.get('reason', ''),
                'status': a.get('status', ''),
                'doctor_name': a.get('doctor_name', '')
            })

        print(f"Confirmed appointments found: {len(out)}")
        return JSONResponse(out)
    except Exception as e:
        print('Error fetching confirmed appointments:', e)
        import traceback
        traceback.print_exc()
        return JSONResponse({'error': 'internal error'}, status_code=500)


@router.get('/appointments/{appointment_id}/details')
async def get_appointment_details(appointment_id: str, request: Request):
    """Get full details of an appointment with patient info"""
    session = get_session(request)
    if not session:
        return JSONResponse({'error': 'Not authenticated'}, status_code=401)

    try:
        appointment = db_client.Prueba.Appointment.find_one({'_id': ObjectId(appointment_id)})
        if not appointment:
            return JSONResponse({'error': 'Appointment not found'}, status_code=404)

        # Get patient info
        patient_name = appointment.get('patient_name', '')
        patient_doc = None
        if patient_name:
            # Try to find patient by name
            patient_doc = db_client.Prueba.Patient.find_one({'name': {'$regex': patient_name.split()[0], '$options': 'i'}})

        # Serialize appointment
        result = {
            'id': str(appointment.get('_id')),
            'patient_name': patient_name,
            'time': appointment.get('time', ''),
            'date': appointment.get('date').isoformat() if isinstance(appointment.get('date'), datetime) else (appointment.get('date') or ''),
            'reason': appointment.get('reason', ''),
            'status': appointment.get('status', ''),
            'doctor_name': appointment.get('doctor_name', ''),
            'patient': None
        }

        if patient_doc:
            result['patient'] = {
                'id': str(patient_doc.get('_id')),
                'name': patient_doc.get('name', ''),
                'surname': patient_doc.get('surname', ''),
                'dui': patient_doc.get('dui', ''),
                'email': patient_doc.get('email', ''),
                'phone': patient_doc.get('phone', ''),
                'birth_date': patient_doc.get('birth_date').isoformat() if isinstance(patient_doc.get('birth_date'), datetime) else (patient_doc.get('birth_date') or ''),
                'file_number': patient_doc.get('file_number', ''),
                'gender': patient_doc.get('gender', ''),
                'blood_type': patient_doc.get('blood_type', ''),
                'allergies': patient_doc.get('allergies', ''),
                'chronic_diseases': patient_doc.get('chronic_diseases', ''),
                'address': patient_doc.get('address', '')
            }

        print(f"Appointment details retrieved: {result['id']}")
        return JSONResponse(result)
    except Exception as e:
        print('Error fetching appointment details:', e)
        import traceback
        traceback.print_exc()
        return JSONResponse({'error': 'internal error'}, status_code=500)


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


# Secondary router without prefix for consultations
consultations_router = APIRouter()

@consultations_router.get('/consultations', response_class=HTMLResponse)
async def consultations_page_no_prefix(request: Request):
    """Render consultations page (no prefix)"""
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


# Add the secondary router to the main router list
router.include_router(consultations_router)