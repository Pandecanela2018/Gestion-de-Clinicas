from fastapi import FastAPI
from routers import doctor,patient,file,schedule,appointment

app = FastAPI()

app.include_router(doctor.router)

app.include_router(patient.router)

app.include_router(file.router)

app.include_router(schedule.router)

app.include_router(appointment.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}