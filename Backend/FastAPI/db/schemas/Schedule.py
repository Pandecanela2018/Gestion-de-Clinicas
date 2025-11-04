def schedule_schema(schedule) -> dict:
    return {"id": str(schedule["_id"]),
            "doctor_name": schedule["doctor_name"],
            "day": schedule["day"],
            "hour_start": schedule["hour_start"],
            "hour_end": schedule["hour_end"]}

def schedules_schema(schedules) -> list:
    return [schedule_schema(schedule) for schedule in schedules]

#prueba