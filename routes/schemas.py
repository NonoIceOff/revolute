from pydantic import BaseModel, EmailStr
from datetime import date

class CreateUser(BaseModel):
    firstname: str
    lastname: str 
    email: EmailStr
    password: str

class CreateAccount(BaseModel):
    user_id: int
    number: str 
    balance: float
    is_principal: bool
    is_closed: bool
    creation_date: date

class CreateTransactions(BaseModel):
    account_by_id: int
    account_to_id: int
    balance: float
    motif: str
    creation_date: date
    is_chancelled: bool

class CreateDeposits(BaseModel):
    account_id: int
    earn: float
    motif: str