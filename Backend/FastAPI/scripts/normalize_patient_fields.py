"""
Normalize patient fields: convert medications, chronic_diseases, allergies from string to list
if they exist and are not already lists.
"""
import json
from pymongo import MongoClient

db_client = MongoClient()

# Get all patients
patients = list(db_client.Prueba.Patient.find({}))
print(f'Total patients: {len(patients)}')

updates_count = 0

for patient in patients:
    patient_id = patient.get('_id')
    updates_needed = {}
    
    # Check medications
    if 'medications' in patient and patient['medications'] is not None and not isinstance(patient['medications'], list):
        val = patient['medications']
        updates_needed['medications'] = [val] if val else []
        print(f"  medications: {val} -> list")
    
    # Check chronic_diseases
    if 'chronic_diseases' in patient and patient['chronic_diseases'] is not None and not isinstance(patient['chronic_diseases'], list):
        val = patient['chronic_diseases']
        updates_needed['chronic_diseases'] = [val] if val else []
        print(f"  chronic_diseases: {val} -> list")
    
    # Check allergies
    if 'allergies' in patient and patient['allergies'] is not None and not isinstance(patient['allergies'], list):
        val = patient['allergies']
        updates_needed['allergies'] = [val] if val else []
        print(f"  allergies: {val} -> list")
    
    if updates_needed:
        print(f"Updating Patient {patient_id}:")
        db_client.Prueba.Patient.update_one({'_id': patient_id}, {'$set': updates_needed})
        updates_count += 1

print(f'\nNormalization complete. Updated {updates_count} patients.')
