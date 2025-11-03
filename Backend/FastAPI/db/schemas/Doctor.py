def doctor_schema(doctor) -> dict:
    return {"id": str(doctor["_id"]),
            "name": doctor["name"],
            "surname": doctor["surname"],
            "Horario_ID_Ref": doctor["Horario_ID_Ref"],
            "speciality": doctor["speciality"],
            "email": doctor["email"],
            "cellphone": doctor["cellphone"]}

