from fastapi import APIRouter, FastAPI, Depends
from sqlmodel import Session, select 
from passlib.hash import sha256_crypt
from .models import User
from .schemas import CreateUser
from .config import *

router = APIRouter()

@router.get("/users")
def read_users(session = Depends(get_session)):
    # users = session.exec(select(User)).all()
    # return users
    return {"Bonjour tout le monde"}

# @router.get("/users")
# def read_users(session = Depends(get_session)):
#     users = session.exec(select(User)).all()
#     return users

@router.post("/login")
def login(email: str, password: str):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == email)).first()
        if not user:
            return {"error": "User not found"}
        if not sha256_crypt.verify(password, user.password):
            return {"error": "Invalid password"}
        return {"token": generate_token(user)}
    

@router.post("/register")
def register(email: str, password: str, lastname: str, firstname: str, session = Depends(get_session)):
    if user:= session.exec(select(User).where(User.email == email)).first():
        return {"error": "User already exists"}
    user = User(email=email, password=sha256_crypt.hash(password), lastname=lastname, firstname=firstname)
    session.add(user)
    session.commit()
    session.refresh(user)

    return {"token": generate_token(user)}