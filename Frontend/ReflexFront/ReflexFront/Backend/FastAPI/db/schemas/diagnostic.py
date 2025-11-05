def diagnostic_schema(diagnostic) -> dict:
    return {"id": str(diagnostic["_id"]),
            "medical_record": diagnostic["medical_record"],
            "date": diagnostic["date"],
            "description": diagnostic["description"],
            "treatment": diagnostic["treatment"]
            }

def diagnostics_schema(diagnostic) -> list:
    return [diagnostic_schema(diagnostic) for diagnostic in diagnostic]