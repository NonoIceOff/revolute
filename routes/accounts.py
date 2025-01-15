from sqlmodel import desc
from math import floor
from fastapi import APIRouter, FastAPI, Depends
from datetime import date, datetime,timedelta
from .schemas import CreateAccount
from .models import Account
from .dependencies import can_create_principal_account
from .config import *


routerAccount = APIRouter()

@routerAccount.post("/open_account")
def open_account(body: CreateAccount, user: dict = Depends(get_user), session = Depends(get_session)):

    user_id = user["id"]
    if user_id is None:
        return {"error": "User not found"}
    
    account = Account(user_id=user_id, name="", iban="", balance=body.balance, is_principal=True, is_closed=False, creation_date=date.today() - timedelta(days=5))
    account.is_principal = can_create_principal_account(user_id, session)
    dt = datetime.now()
    account.iban = "FR2540100001"+str(str(body.user_id)+str(floor(datetime.timestamp(dt)))[3:]).rjust(11, '0')

    session.add(account)
    session.commit()
    session.refresh(account)
    return account

@routerAccount.get("/view_account")
def view_account(account_id: int, user: dict = Depends(get_user), session = Depends(get_session)):
    account = session.exec(select(Account).where(Account.id == account_id)).first()
    if account is None:
        return {"error": "Account not found"}
    return  {"iban": account.iban, "name": account.name ,"balance": account.balance, "creation_date": account.creation_date}

@routerAccount.get("/view_accounts")
def view_accounts(user: dict = Depends(get_user), session = Depends(get_session)):
    user_id = user["id"]
    if user_id is None:
        return {"error": "User not found"}
    accounts = session.exec(select(Account).where(Account.user_id == user["id"]).order_by(desc(Account.creation_date))).all()
    if accounts is None:
        return {"error": "Accounts not found"}
    return [{"iban": account.iban, "name": account.name ,"balance": account.balance, "creation_date": account.creation_date} for account in accounts]