from datetime import date, datetime, timedelta
from math import floor
from fastapi import APIRouter, FastAPI, Depends
from sqlmodel import Session, select 
from passlib.hash import sha256_crypt

from routes.dependencies import can_create_principal_account
from .models import Account, User
from email_validator import validate_email, EmailNotValidError
from .config import *

router = APIRouter()

# def validate_format_email(email: str):
#     try:
#         v = validate_email(email, check_deliverability=True)
#         return {"email": v, "message": "L'email est bon"}
#     except EmailNotValidError as e:
#         return {"message": "L'email n'est pas bon hihiha", "error": e}


@router.get("/users")
def read_users(session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return users

@router.post("/login")
def login(email: str, password: str, session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        return {"error": "User not found"}
    if not sha256_crypt.verify(password, user.password):
        return {"error": "Invalid password"}
    return {"token": generate_token(user)}
    

@router.post("/register")
def register(email: str, password: str, lastname: str, firstname: str, session = Depends(get_session)):
    # v = validate_format_email(email)
    if user:= session.exec(select(User).where(User.email == email)).first():
        return {"error": "User already exists"}
    user = User(email=email, password=sha256_crypt.hash(password), lastname=lastname, firstname=firstname)
    session.add(user)
    session.commit()
    session.refresh(user)

    token = generate_token(user)
    
    # créer un compte principal et rajouter un solde de 100€
    account = Account(user_id=user.id, name="", iban="", balance=100, is_principal=True, is_closed=False, creation_date=date.today() - timedelta(days=5))
    account.is_principal = can_create_principal_account(user.id, session)
    dt = datetime.now()
    account.iban = "FR2540100001"+str(str(user.id)+str(floor(datetime.timestamp(dt)))[3:]).rjust(11, '0')
    session.add(account)
    session.commit()
    session.refresh(account)

    return {"token": token}