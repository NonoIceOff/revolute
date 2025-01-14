from fastapi import APIRouter, FastAPI, Depends
from .schemas import CreateAccount
from .models import Account
from .config import *
from .dependencies import can_create_principal_account
from datetime import date, datetime
from math import floor


routerAccount = APIRouter()

@routerAccount.post("/open_account")
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

@routerAccount.get("/view_account")
def view_account(account_id: int, user: dict = Depends(get_user), session = Depends(get_session)):
    account = session.exec(select(Account).where(Account.id == account_id)).first()
    if account is None:
        return {"error": "Account not found"}
    return  {"number": account.number, "balance": account.balance, "creation_date": account.creation_date}