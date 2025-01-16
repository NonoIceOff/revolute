from fastapi import APIRouter, FastAPI, Depends, HTTPException
from routes.config import *
from routes.users import router
from routes.accounts import routerAccount
from routes.deposit import routerDeposit
from routes.transactions import routerTransactions
from routes.cronjobs import distribution, surplus
from apscheduler.schedulers.background import BackgroundScheduler


# Models
app = FastAPI()
app.include_router(router)
app.include_router(routerAccount)
app.include_router(routerDeposit)
app.include_router(routerTransactions)

scheduler = BackgroundScheduler()

# Startup event
@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    scheduler.add_job(distribution, trigger = "interval", seconds = 5)
    scheduler.start()
    
@app.on_event("shutdown")
def on_shutdown():
    scheduler.shutdown()

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur Revoluto!"}

@app.get("/me")
def me(user: dict = Depends(get_user)):
    return {"id": user["id"],"email": user["email"], "firstname": user["firstname"], "lastname": user["lastname"]}
        