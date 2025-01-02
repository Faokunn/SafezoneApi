from fastapi import FastAPI
from database.db_setup import create_tables
from controllers.user_controller import router as user_router
from controllers.incident_report_controller import router as incident_report_router
from controllers.admin_incident_report_controller import router as admin_incident_report_router


app = FastAPI()
app.add_event_handler("startup", create_tables)

app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(incident_report_router, prefix="/incident-report", tags=["Incident Report"])
app.include_router(admin_incident_report_router, prefix="/admin-incident-report", tags=["Admin Incident Report"])

@app.get("/")
async def root():
    return {"message": "Welcome to the SafeZone API"}