from fastapi import APIRouter, FastAPI, Depends
from typing import TypedDict
from pydantic import BaseModel, EmailStr
from sqlmodel import Session, create_engine, Field, SQLModel, select
import jwt
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from routes.config import *
from routes.users import router

app = FastAPI()
app.include_router(router);


# Configuration mettre dans un fichier de configuration. 
# config = {"version": "1.0.0", "name": "POV"}

# sqlite_file_name = "database.db"
# sqlite_url = f"sqlite:///{sqlite_file_name}"
# connect_args = {"check_same_thread": False}
# engine = create_engine(sqlite_url, connect_args=connect_args)

# secret_key = "very_secret_key"
# algorithm = "HS256"

# bearer_scheme = HTTPBearer()



# Models
# class CreateUser(BaseModel):
#     firstname: str
#     lastname: str 
#     email: EmailStr
#     password: str
#     # token: str

# class CreateAccount(BaseModel):
#     user_id: int
#     number: str 
#     balance: float
#     is_principal: bool
#     is_closed: bool
#     creation_date: date

# class CreateTransactions(BaseModel):
#     user_id: int
#     account_by_id: int
#     account_to_id: int
#     balance: float
#     description: str
#     creation_date: date
#     is_chancelled: bool

# Création des tables 
# class User(SQLModel, table=True):
#     id: int | None = Field(default=None, primary_key=True)
#     firstname: str = Field(min_length=1, max_length=255)
#     lastname: str = Field(min_length=1, max_length=255)
#     email: str = Field(min_length=1, unique=True, max_length=255)
#     password: str = Field(min_length=1, max_length=255)
#     # phone: int = Field(max_length=9)


# class Account(SQLModel, table=True):
#     id: int | None = Field(default=None, primary_key=True)
#     user_id: int = Field(foreign_key="user.id")
#     number: str = Field(max_length=255)
#     balance: float = Field(default=0)
#     is_principal: bool = Field(default=False)
#     is_closed: bool = Field(default=False)
#     creation_date: date = Field(default=date.today())


# class Transactions(SQLModel, table=True):
#     id: int | None = Field(default=None, primary_key=True)
#     user_id: int = Field(default=None, foreign_key="user.id")
#     account_by_id: int = Field(default=None, foreign_key="account.id")
#     account_to_id: int = Field(default=None, foreign_key="account.id")
#     balance: float = Field(default=0)
#     description: str = Field(max_length=255)
#     creation_date: date = Field(default=date.today())
#     is_chancelled: bool = Field(default=False)

    

# def create_db_and_tables():
#     SQLModel.metadata.create_all(engine)

# def get_session():
#     with Session(engine) as session:
#         yield session

# Dependency


# Startup event
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
def read_root():
    return {"message": "Welcome sur FastAPI !"}


@app.get("/me")
def me(token: dict = Depends(get_user)):
    if token:
        return {"id": token["id"],"email": token["email"], "firstname": token["firstname"], "lastname": token["lastname"]}
    
# @app.get("/users/")
# def read_users(session = Depends(get_session)):
#     users = session.exec(select(User)).all()
#     return users


# @app.post("/login")
# def login(email: str, password: str):
#     with Session(engine) as session:
#         user = session.exec(select(User).where(User.email == email)).first()
#         if not user:
#             return {"error": "User not found"}
#         if not sha256_crypt.verify(password, user.password):
#             return {"error": "Invalid password"}
#         return {"token": generate_token(user)}

# @app.post("/register")
# def register(user: CreateUser, session = Depends(get_session)):
#     if user:= session.exec(select(User).where(User.email == User.email)).first():
#         return {"error": "User already exists"}
#     user = User(email= user.email, password=sha256_crypt.hash(user.password), lastname=user.lastname, firstname=user.firstname)
#     session.add(user)
#     session.commit()
#     session.refresh(user)

#     return {"token": generate_token(user)}

