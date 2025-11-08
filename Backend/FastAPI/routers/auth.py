from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from utils.session import set_session, clear_session
from utils.security import verify_password
from db.client import db_client
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

router = APIRouter()

@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
def login(request: Request, dui: str = Form(...), password: str = Form(...)):
    user = db_client.Prueba.Patient.find_one({"dui": dui})

    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Usuario no encontrado"})

    if not verify_password(password, user["password"]):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Contraseña incorrecta"})

    # Si pasa validación → crear sesión
    response = RedirectResponse("/dashboard", 302)
    set_session(response, {"user_id": str(user["_id"]), "dui": dui})
    return response

@router.get("/logout")
def logout():
    response = RedirectResponse("/login", 302)
    clear_session(response)
    return response
