from fastapi import APIRouter, FastAPI, Depends
from sqlmodel import Session, select 
from passlib.hash import sha256_crypt
from .models import User
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
    return {"token": generate_token(user)}