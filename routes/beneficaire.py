from fastapi import APIRouter, FastAPI, Depends
from .schemas import CreateBeneficiary
from .models import Account, Deposits, Transactions, Beneficiary
from .config import *
from .dependencies import ceiling_account
from datetime import date, datetime
from fastapi import FastAPI, HTTPException
from math import floor
from sqlmodel import Session, desc, select 

routerBeneficiary = APIRouter()

@routerBeneficiary.post("/add_benef", tags=["Deposits"])
def create_benef(body: CreateBeneficiary, user: dict = Depends(get_user), session = Depends(get_session)):
    user_id = user["id"]
    bank_account_benef = session.exec(select(Account).where(Account.iban == body.iban)).first()

    if bank_account_benef is None:
        raise HTTPException(status_code=404, detail="No no no iban does not exist")
    
    if user_id == bank_account_benef.user_id :
         raise HTTPException(status_code=404, detail="No, no, no, you can't be a beneficiary")
    
    if bank_account_benef.is_principal == False:
         raise HTTPException(status_code=404, detail="The account is secondary. You must enter a principal account.")
    
    beneficiary = Beneficiary(user_id=user_id, account_beneficiary= bank_account_benef.id)

    session.add(beneficiary)
    session.commit()
    session.refresh(beneficiary)
    return beneficiary

# liste de tous les bénéficiaires de la personne
@routerBeneficiary.get("/view_beneficiaries", tags=["Accounts"])
def view_accounts(user: dict = Depends(get_user), session: Session = Depends(get_session)):
    beneficiaries = session.exec(
        select(Beneficiary).where(
            Beneficiary.user_id == user["id"]
        ).order_by(desc(Beneficiary.creation_date))
    ).all()
    
    if not beneficiaries:
        raise HTTPException(status_code=404, detail="No account found owned by you")
    
    beneficiaries_details = []
    for beneficiary in beneficiaries:
        beneficiaries_details.append({
            "id": beneficiary.id ,
            "user_id": beneficiary.user_id,
            "account_beneficiary": beneficiary.account_beneficiary,
            "bank_account_beneficiary_iban": beneficiary.account.iban,
            "bank_account_beneficiary_name": beneficiary.account.name,
            "creation_date": beneficiary.creation_date,
        })
    
    return beneficiaries_details
