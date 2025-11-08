from fastapi import APIRouter, Request, Form,status
from fastapi.responses import RedirectResponse
from utils.session import set_session, clear_session
from utils.security import verify_password
from db.client import db_client
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

router = APIRouter(prefix="/dashboard_user",
                   tags=["dashboard_user"],
                   responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}})