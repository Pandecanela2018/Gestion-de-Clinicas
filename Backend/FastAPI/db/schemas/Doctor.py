def doctor_schema(doctor) -> dict:
    return {"id": str(doctor["_id"]),
            "name": doctor["name"],
            "surname": doctor["surname"],
            "speciality": doctor["speciality"],
            "email": doctor["email"],
            "phone": doctor["phone"],
            "dui": doctor["dui"]}

def doctors_schema(doctors) -> list:
    return [doctor_schema(doctor) for doctor in doctors]