from pydantic import BaseModel, EmailStr

class CreateUser(BaseModel):
    firstname: str
    lastname: str 
    email: EmailStr
    password: str

class LoginUser(BaseModel):
    email: EmailStr
    password: str

class CreateAccount(BaseModel):
    user_id: int
    type_id: int
    name: str
    balance: float
    is_closed: bool

class CreateTransactions(BaseModel):
    account_by_id: int
    account_to_id: int
    balance: float
    motif: str

class CreateVirements(BaseModel):
    account_by_id: int
    account_to_id: int
    balance: float
    motif: str

class CreateBeneficiary(BaseModel):
    iban: str

class CreateDeposits(BaseModel):
    account_id: int
    earn: float
    motif: str

class PasswordUpdate(BaseModel):
    password: str
    new_password: str