from fastapi import FastAPI
from routers import doctor

app = FastAPI()

app.include_router(doctor.router)
