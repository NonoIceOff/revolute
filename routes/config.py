from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, create_engine, Field, SQLModel, select
from fastapi import APIRouter, FastAPI, Depends
import jwt
from .models import AccountTypes, User

#Configuration. 
config = {"version": "1.0.0", "name": "POV"}

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

secret_key = "very_secret_key"
algorithm = "HS256"

bearer_scheme = HTTPBearer()

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    insert_accounts_types()

def get_session():
    with Session(engine) as session:
        yield session

def get_user(authorization: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    return jwt.decode(authorization.credentials, secret_key, algorithms=[algorithm])

def generate_token(user: User):
    return jwt.encode(user.dict(), secret_key, algorithm=algorithm)

def insert_accounts_types():
    with Session(engine) as session:
        account_types = ["Principal", "Livret A", "Voiture", "Maison", "Autre"]
        existing_types = session.exec(select(AccountTypes).where(AccountTypes.name.in_(account_types))).all()
        existing_type_names = {account_type.name for account_type in existing_types}

        for account_type in account_types:
            if account_type not in existing_type_names:
                new_account_type = AccountTypes(name=account_type)
                session.add(new_account_type)

        session.commit()