from fastapi import APIRouter, FastAPI, Depends
from .schemas import CreateDeposits
from .models import Account, Deposits, Transactions
from .config import *
from .dependencies import ceiling_account
from datetime import date, datetime
from fastapi import FastAPI, HTTPException
from math import floor
from sqlmodel import Session, desc, select 


routerDeposit = APIRouter()

def ceiling_acc(account: Account, sold: float, session = Session):
    account.balance += sold
    deposit = Deposits(account=account.id, earn=sold, motif="Depot", creation_date=datetime.now())
    
    session.add(deposit)
    session.commit()
    session.refresh(deposit)

    if (account.is_principal == False):
        surplus = account.balance - 50000
        if(surplus > 0):
            principal_account = session.exec(select(Account).where(Account.user_id == account.user_id, Account.is_principal == True)).first()
            account.balance = 50000
            ###
            transaction = Transactions(account_by_id = account.id, account_to_id=principal_account.id, balance = surplus, motif= "Surplus", is_cancelled = False, is_pending= True, is_confirmed=False) 
            ###
            session.add(transaction)
            session.add(account)
            session.commit()
            session.refresh(principal_account, transaction)
            return("surplus ajouter au compte principal", surplus)
        else:
            return("sold mis à jour", account.balance)
    else:
        session.add(account)
        session.commit()
        session.refresh(account)
        


@routerDeposit.post("/deposit", tags=["Deposits"])
def create_deposit(body: CreateDeposits, session = Depends(get_session)):
    if body.account_id is None:
        raise HTTPException(status_code=404, detail="Account not found")

    if body.earn <= 0:
        raise HTTPException(status_code=404, detail="The balance must be greater than 0")
    
    if body.account_id:
        account = session.exec(select(Account).where(Account.id == body.account_id)).first()

        ceiling_acc(account, body.earn, session)

        return {"message": "Deposit created successfully", "data": body}
    
# Depots d'un compte bancaire
@routerDeposit.get("/account/deposits", tags=["Deposits"])
def account_deposits(account_id: int, user: dict = Depends(get_user), session: Session = Depends(get_session)):
    deposits = session.exec(
        select(Deposits).where(
            (Deposits.account == account_id)
        ).order_by(desc(Deposits.creation_date))
    ).all()

    if not deposits:
        raise HTTPException(status_code=404, detail="No deposits found for this account")

    return [
        {
            "id": deposit.id,
            "account_id": deposit.account,
            "price": deposit.earn,
            "date": deposit.creation_date,
            "motif": deposit.motif
        }
        for deposit in deposits
    ]