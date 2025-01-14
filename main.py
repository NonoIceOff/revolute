from math import floor
from fastapi import APIRouter, FastAPI, Depends, HTTPException
from typing import TypedDict
from pydantic import BaseModel
from sqlmodel import Session, create_engine, Field, SQLModel, select
from datetime import date, datetime
from routes.config import *
from routes.users import router
from routes.schemas import CreateAccount
from routes.models import Account

app = FastAPI()


# Models
app = FastAPI()
app.include_router(router);





@app.get("/")
def read_root():
    return {"message": "Bienvenue sur FastAPI !"}

@app.get("/users/")
def read_users(session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return users

# Startup event
@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/me")
def me(user: dict = Depends(get_user)):
    return {"id": user["id"],"email": user["email"], "firstname": user["firstname"], "lastname": user["lastname"]}
    
@app.post("/open_account")
def open_account(body: CreateAccount, user: dict = Depends(get_user), session = Depends(get_session)):

    user_id = user["id"]
    if user_id is None:
        return {"error": "User not found"}
    
    account = Account(user_id=body.user_id, number="", is_principal=True, is_closed=False, creation_date=date.today())
    account.is_principal = can_create_principal_account(user_id, session)
    dt = datetime.now()
    account.number = "FR2540100001"+str(str(body.user_id)+str(floor(datetime.timestamp(dt)))[3:]).rjust(11, '0')

    session.add(account)
    session.commit()
    session.refresh(account)
    return account

   
def can_create_principal_account(user_id : int, session = Session)-> bool:
    return not session.exec(select(Account.is_principal).where(Account.user_id == user_id, Account.is_principal == True)).first()