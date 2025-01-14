from fastapi import APIRouter, FastAPI, Depends, HTTPException
from routes.config import *
from routes.users import router
from routes.accounts import routerAccount
from routes.deposit import routerDeposit
from routes.transactions import routerTransactions

# Models
app = FastAPI()
app.include_router(router)
app.include_router(routerAccount)
app.include_router(routerDeposit)
app.include_router(routerTransactions)

# Startup event
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur FastAPI !"}

@app.get("/me")
def me(user: dict = Depends(get_user)):
    return {"id": user["id"],"email": user["email"], "firstname": user["firstname"], "lastname": user["lastname"]}
        