from fastapi import FastAPI
from routers import doctor,patient
from routers import schedule
from routers import appointment

app = FastAPI()

app.include_router(doctor.router)

app.include_router(schedule.router)

app.include_router(appointment.router)

app.include_router(patient.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}