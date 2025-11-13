import sys
import argparse
import json
from pymongo import MongoClient
from bson import ObjectId

# Connect directly to MongoDB
db_client = MongoClient()

parser = argparse.ArgumentParser(description='Inspect Appointment/Patient/Consultation records')
parser.add_argument('--appointment', '-a', help='Appointment _id to inspect')
parser.add_argument('--patient', '-p', help='Patient _id to inspect')
args = parser.parse_args()

if not args.appointment and not args.patient:
    print('Provide --appointment <id> or --patient <id>')
    sys.exit(1)

def to_serializable(obj):
    """Convert BSON types to JSON-serializable formats"""
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):
        return {k: to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [to_serializable(item) for item in obj]
    elif hasattr(obj, 'isoformat'):  # datetime
        return obj.isoformat()
    else:
        return obj

if args.appointment:
    aid = args.appointment
    try:
        a_oid = ObjectId(aid)
    except Exception:
        a_oid = aid
    
    appointment = db_client.Prueba.Appointment.find_one({'_id': a_oid})
    print('--- Appointment ---')
    print(json.dumps(to_serializable(appointment), indent=2))
    
    # try to get patient id from appointment
    pid = None
    if appointment:
        pid = appointment.get('patient_id') or appointment.get('patient') or appointment.get('patientName') or appointment.get('patient_name')
        print('\nDerived patient reference from appointment:', pid)

    if pid:
        try:
            p_oid = ObjectId(pid)
        except Exception:
            p_oid = pid
        
        patient = db_client.Prueba.Patient.find_one({'_id': p_oid})
        print('\n--- Patient (from appointment) ---')
        print(json.dumps(to_serializable(patient), indent=2))
        
        # consultations for patient
        consults = list(db_client.Prueba.Consultation.find({'$or': [{'patient_id': p_oid}, {'patient_id': str(p_oid)}]}).sort('created_at', -1).limit(10))
        print('\n--- Last consultations for patient ---')
        print(json.dumps(to_serializable(consults), indent=2))
    else:
        print('\nNo patient reference found inside appointment.\n')

if args.patient:
    pid = args.patient
    try:
        p_oid = ObjectId(pid)
    except Exception:
        p_oid = pid
    
    patient = db_client.Prueba.Patient.find_one({'_id': p_oid})
    print('\n--- Patient (by id) ---')
    print(json.dumps(to_serializable(patient), indent=2))
    
    consults = list(db_client.Prueba.Consultation.find({'$or': [{'patient_id': p_oid}, {'patient_id': str(p_oid)}]}).sort('created_at', -1).limit(20))
    print('\n--- Last consultations for patient ---')
    print(json.dumps(to_serializable(consults), indent=2))

print('\nDone.')
