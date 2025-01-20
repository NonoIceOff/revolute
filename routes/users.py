from sqlmodel import  select 
from routes.dependencies import can_create_principal_account
from passlib.hash import sha256_crypt
from math import floor
from fastapi import APIRouter,  Depends
from datetime import date, datetime, timedelta

from routes.schemas import CreateUser, LoginUser
from .models import Account, User
from fastapi import HTTPException
from .config import *

router = APIRouter()

@router.get("/users")
def read_users(session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return [{"id": user.id ,"email": user.email, "lastname": user.lastname, "firstname": user.firstname} for user in users]

@router.post("/login", tags=["Authentification"])
def login(body: LoginUser, session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == body.email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not sha256_crypt.verify(body.password, user.password):
        raise HTTPException(status_code=404, detail="Invalid password")
    return {"token": generate_token(user)}
    

@router.post("/register", tags=["Authentification"])
def register(body: CreateUser, session = Depends(get_session)):
    if user:= session.exec(select(User).where(User.email == body.email)).first():
        raise HTTPException(status_code=404, detail="User already exists")
    user = User(email=body.email, password=sha256_crypt.hash(body.password), lastname=body.lastname, firstname=body.firstname)
    session.add(user)
    session.commit()
    session.refresh(user)

    token = generate_token(user)
    
    account = Account(user_id=user.id, name="Compte Depot", iban="", balance=100, is_principal=True, is_closed=False, creation_date=date.today() - timedelta(days=5))
    account.is_principal = can_create_principal_account(user.id, session)
    dt = datetime.now()
    account.iban = "FR2540100001"+str(str(user.id)+str(floor(datetime.timestamp(dt)))[3:]).rjust(11, '0')
    session.add(account)
    session.commit()
    session.refresh(account)
    return {"token": token}