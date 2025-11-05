from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Annotated

# Importar los esquemas definidos
from schemas.auth import LoginRequest, Token

# Asumiendo que tienes un modelo de usuario para la base de datos
# Si no, puedes definirlo aquí o en un archivo db/models/user.py
from pydantic import BaseModel

class UserInDB(BaseModel):
    dui: str
    hashed_password: str
    full_name: Optional[str] = None
    email: Optional[str] = None

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}}
)

# Contexto para el hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Simulación de base de datos de usuarios ---
# En una aplicación real, esto se obtendría de MongoDB
users_db = {
    "06915275-9": {
        "dui": "06915275-9",
        "hashed_password": pwd_context.hash("Cacahuatique64"), # ¡Hashear la contraseña!
        "full_name": "Fran",
        "email": "fran@example.com",
    },
    "12345678-9": {
        "dui": "12345678-9",
        "hashed_password": pwd_context.hash("password"),
        "full_name": "Usuario de Prueba",
        "email": "test@example.com",
    },
}

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(dui: str):
    user_data = users_db.get(dui)
    if user_data:
        return UserInDB(**user_data)
    return None

# --- Generación de Token (simplificado para el ejemplo) ---
# En una aplicación real, usarías una librería como `python-jose` para JWTs
SECRET_KEY = "tu-clave-secreta-super-segura" # ¡CAMBIA ESTO EN PRODUCCIÓN!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    # Aquí iría la lógica real de codificación JWT (ej. `jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)`)
    return f"dummy_jwt_token_for_{to_encode['sub']}_exp_{expire.isoformat()}"

# --- Endpoint de Login ---
@router.post("/login", response_model=Token)
async def login_for_access_token(login_request: LoginRequest):
    user = get_user(login_request.dui)
    if not user or not verify_password(login_request.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="DUI o contraseña incorrectos.")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.dui}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}