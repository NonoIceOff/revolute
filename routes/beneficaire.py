from fastapi import APIRouter, FastAPI, Depends
from .schemas import CreateBeneficiary
from .models import Account, Deposits, Transactions, Beneficiary
from .config import *
from .dependencies import ceiling_account
from datetime import date, datetime
from fastapi import FastAPI, HTTPException
from math import floor
from sqlmodel import Session, select 

routerBeneficiary = APIRouter()

@routerBeneficiary.post("/add_benef", tags=["Deposits"])
def create_benef(body: CreateBeneficiary, session = Depends(get_session)):
    benef = session.exec(select(Account).where(Account.iban == body.iban)).first()

    if benef is None:
        raise HTTPException(status_code=404, detail="Non non non l'iban n'existe pas")
    
    if body.user_id == benef.user_id :
         raise HTTPException(status_code=404, detail="Non non non tu peux pas te mettre en bénéficiaire")
    
    beneficiary = Beneficiary(user_id=body.user_id, user_account_beneficiary= body.user_account_beneficiary)

    session.add(beneficiary)
    session.commit()
    session.refresh(beneficiary)
    return beneficiary