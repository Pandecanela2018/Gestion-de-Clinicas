from fastapi import APIRouter, HTTPException, status
from db.models.file import File
from db.schemas.file import file_schema
from db.client import db_client
from bson import ObjectId

router = APIRouter(prefix="/file",
                   tags=["file"],
                   responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}})

@router.post("/", response_model=File, status_code=status.HTTP_201_CREATED)
async def file(file: File):
    if type(search_file("file_number", file.file_number)) == File:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="El usuario ya existe"
        )

    file_dict = dict(file)
    del file_dict["id"]

    id = db_client.Prueba.File.insert_one(file_dict).inserted_id

    new_file = file_schema(db_client.Prueba.File.find_one({"_id": id}))

    return File(**new_file)


def search_file(field: str, key):
    try:
        file = db_client.Prueba.File.find_one({field: key})
        return File(**file_schema(file))
    except:
        return{"error": "No se ha encontrado el usuario"}