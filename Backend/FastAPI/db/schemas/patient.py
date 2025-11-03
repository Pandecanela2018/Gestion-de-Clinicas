def patient_schema(patient) -> dict:
    return {"id": str(patient["_id"]),
            "name": patient["name"],
            "surname": patient["surname"],
            "email": patient["email"],
            "dui": patient["dui"],
            "birth_date": patient["birth_date"],
            "file_number": patient["file_number"],
            "phone": patient["phone"]}

def patients_schema(patients) -> list:
    return [patient_schema(patient) for patient in patients]