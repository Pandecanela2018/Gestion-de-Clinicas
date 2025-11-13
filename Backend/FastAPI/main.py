from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import doctor, patient, file, schedule, appointment, diagnostic, admin, auth, dashboard_user, calendario, agendar, receta, historial, doctor_auth, dashboard_doctor, patients_doctor, consultations, expedientes
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory="templates")

# Define la ruta al directorio 'static'
app.mount("/static", StaticFiles(directory="static"), name="static")

# IMPORTANTE: Incluir doctor routers PRIMERO
app.include_router(doctor_auth.router)
app.include_router(dashboard_doctor.router)
app.include_router(patients_doctor.router)
app.include_router(consultations.router)
app.include_router(expedientes.router)

# Luego los otros routers
app.include_router(doctor.router)
app.include_router(auth.router)
app.include_router(patient.router)
app.include_router(file.router)
app.include_router(schedule.router)
app.include_router(appointment.router)
app.include_router(diagnostic.router)
app.include_router(admin.router)
app.include_router(dashboard_user.router)
app.include_router(agendar.router)
app.include_router(calendario.router)
app.include_router(receta.router)
app.include_router(historial.router)