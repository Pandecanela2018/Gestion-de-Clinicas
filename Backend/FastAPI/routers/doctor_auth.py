from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from utils.session import set_session, clear_session
from utils.security import verify_password
from db.client import db_client
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

router = APIRouter()

@router.get("/login-doctor")
def login_doctor_page(request: Request):
    return templates.TemplateResponse("login_doctor.html", {"request": request})

@router.post("/login-doctor")
def login_doctor(request: Request, dui: str = Form(...), password: str = Form(...)):
    doctor = db_client.Prueba.Doctor.find_one({"dui": dui})

    if not doctor:
        return templates.TemplateResponse("login_doctor.html", {"request": request, "error": "DUI o contraseña incorrectos"})

    if not verify_password(password, doctor["password"]):
        return templates.TemplateResponse("login_doctor.html", {"request": request, "error": "DUI o contraseña incorrectos"})

    # Si pasa validación → crear sesión
    response = RedirectResponse("/dashboard-doctor", 302)
    set_session(response, {"doctor_id": str(doctor["_id"]), "dui": dui})
    return response

@router.get("/logout-doctor")
def logout_doctor():
    response = RedirectResponse("/login-doctor", 302)
    clear_session(response)
    return response