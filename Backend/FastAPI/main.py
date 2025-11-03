from fastapi import FastAPI
from Backend.FastAPI.routers.doctor import doctor

app = FastAPI()

app.include_router(doctor.router)
