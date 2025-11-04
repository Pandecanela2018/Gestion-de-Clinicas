def appointment_schema(appointment) -> dict:
    return {"id": str(appointment["_id"]),
            "patient_name": appointment["patient_name"],
            "doctor_name": appointment["doctor_name"],
            "date": appointment["date"],
            "status": appointment["status"]}

def appointments_schema(appointments) -> list:
    return [appointment_schema(appointment) for appointment in appointments]

#prueba