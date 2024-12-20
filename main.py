from fastapi import FastAPI
from database.db_setup import create_tables
from controllers.user_controller import router as user_router

app = FastAPI()
app.add_event_handler("startup", create_tables)

app.include_router(user_router, prefix="/users", tags=["Users"])
@app.get("/")
async def root():
    return {"message": "Welcome to the SafeZone API"}