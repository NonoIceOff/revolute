from pydantic import BaseModel, EmailStr
from datetime import date

class CreateUser(BaseModel):
    firstname: str
    lastname: str 
    email: EmailStr
    password: str

class CreateAccount(BaseModel):
    user_id: int
    name: str
    balance: float
    is_principal: bool
    is_closed: bool

class CreateTransactions(BaseModel):
    account_by_id: int
    account_to_id: int
    balance: float
    motif: str

class CreateDeposits(BaseModel):
    account_id: int
    earn: float
    motif: str