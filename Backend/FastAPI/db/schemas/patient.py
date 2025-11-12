def patient_schema(patient) -> dict:
    return {
        "id": str(patient["_id"]),
        "name": patient["name"],
        "surname": patient["surname"],
        "second_surname": patient.get("second_surname"),
        "email": patient.get("email"),
        "dui": patient["dui"],
        "birth_date": patient["birth_date"],
        "file_number": patient["file_number"],
        "phone": patient["phone"],
        "gender": patient["gender"],
        "address": patient["address"],
        "city": patient["city"],
        "province": patient["province"],
        "postal_code": patient.get("postal_code"),
        "blood_type": patient["blood_type"],
        "allergies": patient.get("allergies"),
        "chronic_diseases": patient.get("chronic_diseases"),
        "medications": patient.get("medications"),
        "emergency_name": patient["emergency_name"],
        "emergency_phone": patient["emergency_phone"],
        "emergency_relation": patient["emergency_relation"],
        "has_insurance": patient.get("has_insurance", False)
    }

def patients_schema(patients) -> list:
    return [patient_schema(patient) for patient in patients]