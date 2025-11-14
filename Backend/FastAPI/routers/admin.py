from fastapi import APIRouter, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from db.models.admin import Admin, AdminP
from db.models.Doctor import Doctor
from db.schemas.admin import admin_schema, admins_schema
from db.schemas.Doctor import doctors_schema
from utils.security import hash_password, verify_password
from utils.session import get_session, set_session, clear_session
from db.client import db_client
from bson import ObjectId

templates = Jinja2Templates(directory="templates")

router = APIRouter(prefix="/admin",
                   tags=["admin"],
                   responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}})

# Admin authentication endpoints (these come first to avoid conflicts)
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Render admin login page"""
    return templates.TemplateResponse("login_admin.html", {"request": request})

@router.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    """Authenticate admin user"""
    admin_doc = db_client.Prueba.Admin.find_one({"username": username})
    
    if not admin_doc:
        return templates.TemplateResponse("login_admin.html", {
            "request": request,
            "error": "Usuario o contraseña incorrectos"
        })
    
    if not verify_password(password, admin_doc.get("password")):
        return templates.TemplateResponse("login_admin.html", {
            "request": request,
            "error": "Usuario o contraseña incorrectos"
        })
    
    # Create session
    response = RedirectResponse(url="/admin/dashboard", status_code=302)
    set_session(response, {"admin_id": str(admin_doc["_id"]), "admin_username": username})
    return response

@router.get("/logout")
async def logout(request: Request):
    """Logout admin user"""
    response = RedirectResponse(url="/admin/login", status_code=302)
    clear_session(response)
    return response

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Admin dashboard with doctor management"""
    session = get_session(request)
    
    if not session or "admin_id" not in session:
        return RedirectResponse(url="/admin/login", status_code=302)
    
    admin_doc = db_client.Prueba.Admin.find_one({"_id": ObjectId(session["admin_id"])})
    admin_data = admin_schema(admin_doc)
    
    # Get all doctors
    doctors = list(db_client.Prueba.Doctor.find())
    doctors_data = doctors_schema(doctors)
    
    return templates.TemplateResponse("dashboard-admin.html", {
        "request": request,
        "admin": admin_data,
        "doctors": doctors_data
    })


def search_admin(field: str, key):
    try:
        admin = db_client.Prueba.Admin.find_one({field: key})
        return Admin(**admin_schema(admin))
    except:
        return{"error": "No se ha encontrado el usuario"}

# Admin CRUD API endpoints (for programmatic access)
@router.get("/api/admins", response_model=list[Admin])
async def get_admins():
    return admins_schema(db_client.Prueba.Admin.find())

@router.get("/api/admins/{id}")
async def get_admin(id: str):
    return search_admin("_id", ObjectId(id))

@router.post("/api/admins", response_model=Admin, status_code=status.HTTP_201_CREATED)
async def create_admin(admin: AdminP):
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

@router.put("/api/admins/{id}", response_model=Admin)
async def update_admin(id: str, admin: AdminP):

    admin_dict = dict(admin)
    if "id" in admin_dict:
        del admin_dict["id"]

    if admin.password:
        admin_dict["password"] = hash_password(admin.password)
    else:
        del admin_dict["password"]

    try:
        db_client.Prueba.Admin.find_one_and_replace({"_id": ObjectId(id)}, admin_dict)
    except:
        return {"error": "No se ha actualizado el usuario"}
    
    return search_admin("_id", ObjectId(id))

@router.delete("/api/admins/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_admin(id: str):
    found = db_client.Prueba.Admin.find_one_and_delete({"_id": ObjectId(id)})

    if not found:
        return {"error": "No se ha eliminado el usuario"}
