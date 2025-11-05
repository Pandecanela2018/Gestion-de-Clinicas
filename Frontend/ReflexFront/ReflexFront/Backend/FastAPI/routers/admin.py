from fastapi import APIRouter, HTTPException, status
from db.models.admin import Admin,AdminP
from db.schemas.admin import admin_schema,admins_schema
from utils.security import hash_password, verify_password
from db.client import db_client
from bson import ObjectId

router = APIRouter(prefix="/admin",
                   tags=["admin"],
                   responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}})

@router.get("/", response_model=list[Admin])
async def admin():
    return admins_schema(db_client.Prueba.Admin.find())

@router.get("/{id}")
async def admin(id: str):
    return search_admin("_id", ObjectId(id))

@router.get("/")
async def admin(id: str):
    return search_admin("_id", ObjectId(id))

@router.post("/", response_model=Admin, status_code=status.HTTP_201_CREATED)
async def admin(admin: AdminP):
    if type(search_admin("email", admin.email)) == Admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="El usuario ya existe"
        )

    admin_dict = dict(admin)
    admin_dict["password"] = hash_password(admin_dict["password"])
    del admin_dict["id"]

    id = db_client.Prueba.Admin.insert_one(admin_dict).inserted_id

    new_admin = admin_schema(db_client.Prueba.Admin.find_one({"_id": id}))

    return Admin(**new_admin)

@router.put("/", response_model=Admin)
async def admin(admin: AdminP):

    admin_dict = dict(admin)
    del admin_dict["id"]

    if admin.password:
        admin_dict["password"] = hash_password(admin.password)
    else:
        del admin_dict["password"]

    try:
        db_client.Prueba.Admin.find_one_and_replace({"_id": ObjectId(admin.id)}, admin_dict)
    except:
        return {"error": "No se ha actualziado el usuario"}
    
    return search_admin("_id", ObjectId(admin.id))

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin(id: str):
    found = db_client.Prueba.Admin.find_one_and_delete({"_id": ObjectId(id)})

    if not found:
        return {"error": "No se ha eliminado el usuario"}


def search_admin(field: str, key):
    try:
        admin = db_client.Prueba.Admin.find_one({field: key})
        return Admin(**admin_schema(admin))
    except:
        return{"error": "No se ha encontrado el usuario"}