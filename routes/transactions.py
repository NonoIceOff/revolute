from asyncio import sleep
from fastapi import APIRouter, FastAPI, Depends
from .schemas import CreateTransactions
from .models import Transactions
from .models import Account
from .config import *
from sqlmodel import desc
from datetime import date, datetime

import time

    #🥝🥝                                    🥝🥝         
    #🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝
    #🥝🥝🥝🥝👁️🥝🥝🥝🥝🥝🥝🥝🥝🥝👁️🥝🥝🥝🥝
    #🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝
    #🥝🥝🥝🥝🥝🥝🦷🦷🦷🦷🦷🦷🦷🥝🥝🥝🥝🥝🥝
    #🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝


routerTransactions = APIRouter()
is_finish = False;

@routerTransactions.post("/history")
def historyTransactions(account_id: int, user: dict = Depends(get_user), session = Depends(get_session)):
        history = session.exec(select(Transactions).where(Transactions.account_by_id == user["id"] ).order_by(desc(Transactions.creation_date))).all()
        print(history)
        return [{"source_account": historys.account_by_id, "destination_account": historys.account_to_id, "price": historys.balance, "date": historys.creation_date, "motif": historys.motif} for historys in history ] 

@routerTransactions.post("/transactions")
def transactions(body: CreateTransactions,  user: dict = Depends(get_user), session = Depends(get_session)):
    user_id = user["id"]
    if user_id is None:
        return {"error": "User not found"}
    
    if body.account_to_id is None:
        return {"error": "Account not found"}
    
    if body.account_to_id:
        accountId_receiver = session.exec(select(Account).where(Account.id == body.account_to_id)).first()
        accountId_sender = session.exec(select(Account).where(Account.id == body.account_by_id)).first()

        if body.balance <= 0:
            return {"error": "Bah nan dcp m'est de l'argent sale radin"}
        
        if accountId_sender.balance <= 0:
            return {"error": "T'es pauvre ahahahahah"}
        

        # accountId_receiver.balance += body.balance
        accountId_sender.balance -= body.balance
        # session.add(accountId_receiver)
        session.add(accountId_sender)
        session.commit()
        # session.refresh(accountId_receiver)
        session.refresh(accountId_sender)
        transaction = Transactions(account_by_id = body.account_by_id, account_to_id=body.account_to_id, balance= body.balance, motif= body.motif, is_cancelled = False, is_pending= True, is_confirmed=False)
        session.add(transaction)
        session.commit()
        session.refresh(transaction)
        return transaction
        
    else:
        return {"error": "Account Not Found"}
    

@routerTransactions.post("/cancel_transaction") 
def cancel_transaction(transaction_id: int, user: dict = Depends(get_user), session = Depends(get_session)):
    transaction = session.exec(select(Transactions).where(Transactions.id == transaction_id)).first()
    account_in_transaction = session.exec(select(Account).where(Account.id == transaction.account_by_id)).first()


    print(transaction)

    if account_in_transaction.user_id != user["id"]:
        return {"error": "Vous n'êtes pas autorisé à annuler cette transaction"}
    
    if transaction is None:
        return {"error": "Transaction not found"}
    
    if transaction.is_pending == False:
        return {"error": "Transaction déjà confirmée"}

    account_in_transaction.balance += transaction.balance
    transaction.is_chancelled = True
    transaction.is_confirmed = False
    session.add(transaction)
    session.add(account_in_transaction)
    session.commit()
    return {"message": "Transaction annulée avec succès"}
