from fastapi import APIRouter, HTTPException, status, Query
from db.models.diagnostic import Diagnostic
from db.schemas.diagnostic import diagnostics_schema,diagnostic_schema
from db.client import db_client
from bson import ObjectId
from datetime import datetime

router = APIRouter()

router = APIRouter(prefix="/diagnostic",
                   tags=["diagnostic"],
                   responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}})

@router.get("/", response_model=list[Diagnostic])
async def diagnostics(medical_record: str | None = Query(None, description="Filtrar por medical_record")):
    """Si se pasa medical_record, filtra por ese valor (acepta string o número). Si no, devuelve todos."""
    if medical_record:
        candidates = [medical_record,]
        try:
            mr_int = int(medical_record)
            candidates.append(mr_int)
            candidates.append(str(mr_int))
        except Exception:
            pass
        cursor = db_client.Prueba.Diagnostic.find({"medical_record": {"$in": candidates}}).sort("date", -1)
        return diagnostics_schema(cursor)
    return diagnostics_schema(db_client.Prueba.Diagnostic.find())

@router.get("/{id}")
async def diagnostic(id: str):
    return search_diagnostic("_id", ObjectId(id))

@router.get("/")
async def diagnostic(id: str):
    return search_diagnostic("_id", ObjectId(id))

@router.post("/", response_model=Diagnostic, status_code=status.HTTP_201_CREATED)
async def diagnostic(diagnostic: Diagnostic):
    existing_diagnostic = db_client.Prueba.Diagnostic.find_one({
        "_id": diagnostic.id,
    })
    
    if existing_diagnostic:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe el expediente"
        )

    diagnostic_dict = dict(diagnostic)
    del diagnostic_dict["id"]

    # Normalize medical_record to int when possible and parse date to datetime
    try:
        if "medical_record" in diagnostic_dict:
            diagnostic_dict["medical_record"] = int(diagnostic_dict["medical_record"])
    except Exception:
        # leave as-is if cannot convert
        pass

    try:
        if "date" in diagnostic_dict and isinstance(diagnostic_dict["date"], str):
            # try ISO format
            diagnostic_dict["date"] = datetime.fromisoformat(diagnostic_dict["date"])
    except Exception:
        # leave as-is
        pass

    id = db_client.Prueba.Diagnostic.insert_one(diagnostic_dict).inserted_id

    new_diagnostic = diagnostic_schema(db_client.Prueba.Diagnostic.find_one({"_id": id}))

    return Diagnostic(**new_diagnostic)

@router.put("/", response_model=Diagnostic)
async def diagnostic(diagnostic: Diagnostic):

    diagnostic_dict = dict(diagnostic)
    del diagnostic_dict["id"]

    # Normalize fields before update as well
    try:
        if "medical_record" in diagnostic_dict:
            diagnostic_dict["medical_record"] = int(diagnostic_dict["medical_record"])
    except Exception:
        pass
    try:
        if "date" in diagnostic_dict and isinstance(diagnostic_dict["date"], str):
            diagnostic_dict["date"] = datetime.fromisoformat(diagnostic_dict["date"])
    except Exception:
        pass

    try:
        db_client.Prueba.Diagnostic.find_one_and_replace({"_id": ObjectId(diagnostic.id)}, diagnostic_dict)
    except Exception:
        return {"error": "No se ha actualizado el diagostico"}
    
    return search_diagnostic("_id", ObjectId(diagnostic.id))


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def diagnostic(id: str):
    found = db_client.Prueba.Diagnostic.find_one_and_delete({"_id": ObjectId(id)})

    if not found:
        return {"error": "No se ha eliminado la cita"}

def search_diagnostic(field: str, key):
    try:
        appointment = db_client.Prueba.Diagnostic.find_one({field: key})
        return Diagnostic(**diagnostic_schema(appointment))
    except:
        return{"error": "No se ha encontrado la cita"}
    
# prueba1