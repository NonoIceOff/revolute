from fastapi import APIRouter, FastAPI, Depends
from .schemas import CreateDeposits
from .models import Account, Deposits
from .config import *
from .dependencies import can_create_principal_account
from datetime import date, datetime
from fastapi import FastAPI, HTTPException
from math import floor

routerDeposit = APIRouter()

@routerDeposit.post("/deposit", tags=["Deposits"])
def create_deposit(body: CreateDeposits, user: dict = Depends(get_user), session = Depends(get_session)):

    if user["id"] is None:
        raise HTTPException(status_code=404, detail="User not found")
        
    
    if body.earn <= 0:
        raise HTTPException(status_code=404, detail="The balance must be greater than 0")
    
    if body.account_id:
        account = session.exec(select(Account).where(Account.id == body.account_id, Account.is_principal == True)).first()
        if account is None:
            raise HTTPException(status_code=404, detail="Account not found or its not a principal account")
        else:
            account.balance += body.earn
            session.add(account)
    
        deposit = Deposits(account=body.account_id, earn=body.earn, motif=body.motif, creation_date=datetime.now())

        session.add(deposit)
        session.commit()
        session.refresh(deposit)
        session.refresh(account)
        
        return {"account": account, "deposit": deposit}
    else:
        raise HTTPException(status_code=404, detail="Account not found")