from math import floor
from fastapi import APIRouter, FastAPI, Depends, HTTPException
from typing import TypedDict
from pydantic import BaseModel
from sqlmodel import Session, create_engine, Field, SQLModel, select
import jwt
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from datetime import date, datetime
from passlib.hash import sha256_crypt

from routes import accounts, transactions, users

app = FastAPI()

# Configuration
config = {"version": "1.0.0", "name": "POV"}

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

secret_key = "very_secret_key"
algorithm = "HS256"

bearer_scheme = HTTPBearer()

# Models
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    firstname: str = Field(max_length=255)
    lastname: str = Field(max_length=255)
    email: str = Field(unique=True,max_length=255)
    password: str = Field(max_length=255)

class CreateUser(BaseModel):
    firstname: str
    lastname: str 
    email: str
    password: str
    token: str

class Account(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    number: str = Field(max_length=255, nullable=True, unique=True)
    balance: float = Field(default=0)
    is_principal: bool = Field(default=False)
    is_closed: bool = Field(default=False)
    creation_date: date = Field(default=date.today())

class CreateAccount(BaseModel):
    user_id: int

class Transactions(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(default=None, foreign_key="user.id")
    account_by_id: int = Field(default=None, foreign_key="account.id")
    account_to_id: int = Field(default=None, foreign_key="account.id")
    balance: float = Field(default=0)
    description: str = Field(max_length=255)
    creation_date: date = Field(default=date.today())
    is_chancelled: bool = Field(default=False)

class CreateTransactions(BaseModel):
    user_id: int
    account_by_id: int
    account_to_id: int
    balance: float
    description: str
    creation_date: date
    is_chancelled: bool
    

# Database utilities
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

# Dependency
def get_user(authorization: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    try:
        return jwt.decode(authorization.credentials, secret_key, algorithms=[algorithm])
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

def generate_token(user: User):
    return jwt.encode(user.dict(), secret_key, algorithm=algorithm)


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

@app.post("/login")
def login(email: str, password: str, session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        return {"error": "User not found"}
    if not sha256_crypt.verify(password, user.password):
        return {"error": "Invalid password"}
    return {"token": generate_token(user)}

@app.post("/register")
def register(email: str, password: str, lastname: str, firstname: str, session = Depends(get_session)):
    if user:= session.exec(select(User).where(User.email == email)).first():
        return {"error": "User already exists"}
    user = User(email=email, password=sha256_crypt.hash(password), lastname=lastname, firstname=firstname)
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"token": generate_token(user)}

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