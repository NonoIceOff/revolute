from sqlmodel import desc
from math import floor
from fastapi import APIRouter, FastAPI, Depends
from datetime import date, datetime,timedelta
from .schemas import CreateAccount
from .models import Account, Transactions
from fastapi import FastAPI, HTTPException
from .dependencies import can_create_principal_account
from .config import *


routerAccount = APIRouter()

@routerAccount.post("/open_account", tags=["Accounts"])
def open_account(body: CreateAccount, user: dict = Depends(get_user), session = Depends(get_session)):

    account = Account(user_id=body.user_id, name=body.name, iban="", balance=body.balance, is_principal=True, is_closed=False, creation_date=date.today() - timedelta(days=5), type_id=1)

    account.is_principal = can_create_principal_account(user["id"], session)

    # if account.is_principal == False:
    #     account.type_id = 2 # Type "Epargne"

    if account.balance > 50000 and account.is_principal == False:
        raise HTTPException(status_code=404, detail="Secondary account must have a maximum balance of 50000")
    

    dt = datetime.now()
    account.iban = "FR2540100001"+str(str(body.user_id)+str(floor(datetime.timestamp(dt)))[3:]).rjust(11, '0')
    session.add(account)
    session.commit()
    session.refresh(account)
    return account

@routerAccount.post("/close_account", tags=["Accounts"])
def close_account(account_id: int, user: dict = Depends(get_user), session: Session = Depends(get_session)):
    
    account = session.exec(select(Account).where(Account.id == account_id)).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    if account.is_principal:
        raise HTTPException(status_code=404, detail="Cannot close principal account")

    pending_transactions = session.exec(select(Transactions).where(
        (Transactions.account_by_id == account_id) | (Transactions.account_to_id == account_id),
        Transactions.is_pending == True
    )).all()
    if pending_transactions:
        raise HTTPException(status_code=404, detail="Account has pending transactions")

    principal_account = session.exec(select(Account).where(Account.user_id == user["id"], Account.is_principal == True)).first()
    if not principal_account:
        raise HTTPException(status_code=404, detail="Principal Account not found")

    principal_account.balance += account.balance
    account.balance = 0
    account.is_closed = True
    session.add(account)
    session.add(principal_account)
    session.commit()
    return {"message": "Account closed successfully"}

@routerAccount.get("/view_account", tags=["Accounts"])
def view_account(account_id: int, user: dict = Depends(get_user), session = Depends(get_session)):
    account = session.exec(select(Account).where(Account.id == account_id, Account.is_closed == False, Account.user_id == user["id"])).first()
    type_name = session.exec(select(AccountTypes).where(AccountTypes.id == account.type_id)).first()
    
    if account is None:
        raise HTTPException(status_code=404, detail="No account found owned by you")
    if account.is_closed:
        raise HTTPException(status_code=404, detail="Account is closed")
    
    return  {"id": account.id ,"iban": account.iban, "name": account.name ,"balance": account.balance, "creation_date": account.creation_date, "type": type_name.name}

@routerAccount.get("/view_account/name", tags=["Accounts"])
def view_account(account_id: int, user: dict = Depends(get_user), session = Depends(get_session)):
    account = session.exec(select(Account).where(Account.id == account_id, Account.is_closed == False, Account.user_id == user["id"])).first()
    
    if account is None:
        raise HTTPException(status_code=404, detail="No account found owned by you")
    if account.is_closed:
        raise HTTPException(status_code=404, detail="Account is closed")
    
    return  {"name": account.name}


@routerAccount.get("/view_accounts", tags=["Accounts"])
def view_accounts(user: dict = Depends(get_user), session: Session = Depends(get_session)):
    accounts = session.exec(
        select(Account).where(
            Account.user_id == user["id"],
            Account.is_closed == False
        ).order_by(Account.creation_date.desc())
    ).all()
    
    if not accounts:
        raise HTTPException(status_code=404, detail="No account found owned by you")
    
    account_details = []
    for account in accounts:
        type_name = session.exec(select(AccountTypes).where(AccountTypes.id == account.type_id)).first()
        account_details.append({
            "id": account.id ,
            "iban": account.iban,
            "name": account.name,
            "balance": account.balance,
            "creation_date": account.creation_date,
            "type": type_name.name
        })
    
    return account_details