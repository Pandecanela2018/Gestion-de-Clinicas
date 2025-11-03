from fastapi import FastAPI
from routers import doctor,patient,file

app = FastAPI()

app.include_router(doctor.router)

app.include_router(patient.router)

app.include_router(file.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}