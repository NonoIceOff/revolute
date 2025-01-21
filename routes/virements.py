from fastapi import APIRouter, Depends
from sqlmodel import desc
from .schemas import CreateVirements
from .models import Virements, Account
from .config import *
from .dependencies import ceiling_account
from fastapi import HTTPException
from sqlmodel import desc

routerVirements = APIRouter()
is_finish = False

@routerVirements.post("/virements/history", tags=["virements"])
def historyVirements(user: dict = Depends(get_user), session = Depends(get_session)):
    user_id = user["id"]
    history = session.exec(select(Virements).where(Virements.account_by_id == user_id ).order_by(desc(Virements.creation_date))).all()
    return [{"source_account": historys.account_by_id, "destination_account": historys.account_to_id, "price": historys.balance, "date": historys.creation_date, "motif": historys.motif} for historys in history ] 

@routerVirements.post("/virements", tags=["virements"])
def virements(body: CreateVirements,  user: dict = Depends(get_user), session = Depends(get_session)):
    if body.account_to_id is None:
         raise HTTPException(status_code=404, detail="Account not found")
    
    user_account_sender = session.exec(select(Account).where(Account.id == body.account_by_id)).first()
    user_account_receiver = session.exec(select(Account).where(Account.id == body.account_to_id)).first()

    if user_account_receiver == user_account_sender:
        raise HTTPException(status_code=404, detail="Vous ne pouvez pas faire de virement avec le même compte.")
    
    if user_account_receiver.user_id == user_account_sender.user_id:
        raise HTTPException(status_code=404, detail="Vous ne pouvez pas faire de virement vers un de vos comptes. Utilisez plutôt une transaction.")

    if user_account_sender.user_id != user["id"]:
        raise HTTPException(status_code=404, detail="You cannot create a virements with an account that does not belong to you")


    accountId_receiver = session.exec(select(Account).where(Account.id == body.account_to_id)).first()
    account_sender = session.exec(select(Account).where(Account.id == body.account_by_id)).first()

    if body.balance <= 0:
        raise HTTPException(status_code=404, detail="You cannot make a virement with a negative amount")
    
    if account_sender.balance <= body.balance:
        raise HTTPException(status_code=404, detail="Insufficient balance")
    
    
    account_sender.balance -= body.balance
    virement = Virements(account_by_id = body.account_by_id, account_to_id=body.account_to_id, balance= body.balance, motif= body.motif, is_cancelled = False, is_pending= True, is_confirmed=False)
    session.add(account_sender)
    session.add(virement)
    session.commit()
    session.refresh(virement, account_sender)
    ceiling_account(accountId_receiver, body.balance, session)
    return virement
    

@routerVirements.post("/virement/cancel", tags=["virements"]) 
def cancel_virements(virement_id: int, user: dict = Depends(get_user), session = Depends(get_session)):
    virement = session.exec(select(Virements).where(Virements.id == virement_id)).first()
    account_in_transaction = session.exec(select(Account).where(Account.id == virement.account_by_id)).first()

    if account_in_transaction.user_id != user["id"]:
        raise HTTPException(status_code=404, detail="You're not allowed to cancel this transaction")
    
    if virement is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    if virement.is_pending == False:
        raise HTTPException(status_code=404, detail="Transaction already confirmed")

    account_in_transaction.balance += virement.balance
    virement.is_chancelled = True
    virement.is_confirmed = False
    virement.is_pending = False
    session.add(virement)
    session.add(account_in_transaction)
    ceiling_account(account_in_transaction, session)
    session.commit()
    session.refresh(virement)
    return virement


@routerVirements.get("/virement/view", tags=["virements"])
def view_transaction(virement_id: int, user: dict = Depends(get_user), session = Depends(get_session)):
    virement = session.exec(select(Virements).where(Virements.id == virement_id)).first()
    account_sender = session.exec(select(Account).where(Account.id == virement.account_by_id)).first()
    account_receiver = session.exec(select(Account).where(Account.id == virement.account_to_id)).first()
    user_sender = account_sender.user_id
    user_receiver = account_receiver.user_id

    if virement is None:
        raise HTTPException(status_code=404, detail="Virement not found")

    if user_sender != user["id"] or user_receiver != user["id"]:
        raise HTTPException(status_code=404, detail="You are not the sender or the receiver of this virement")

    return  {"source_account": virement.account_by_id, "destination_account": virement.account_to_id, "price": virement.balance, "date": virement.creation_date, "motif": virement.motif}