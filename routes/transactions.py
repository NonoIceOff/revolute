from fastapi import APIRouter, FastAPI, Depends
from sqlmodel import desc
from .schemas import CreateTransactions
from .models import Transactions, Account
from .config import *
from .dependencies import ceiling_account
from sqlmodel import desc


    #🥝🥝                                    🥝🥝         
    #🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝
    #🥝🥝🥝🥝👁️🥝🥝🥝🥝🥝🥝🥝🥝🥝👁️🥝🥝🥝🥝
    #🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝
    #🥝🥝🥝🥝🥝🥝🦷🦷🦷🦷🦷🦷🦷🥝🥝🥝🥝🥝🥝
    #🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝


routerTransactions = APIRouter()
is_finish = False

@routerTransactions.post("/history")
def historyTransactions(account_id: int, user: dict = Depends(get_user), session = Depends(get_session)):
    if user["id"] is None:
        return {"error": "User not found"}
    user_id = user["id"]
    history = session.exec(select(Transactions).where(Transactions.account_by_id == user_id ).order_by(desc(Transactions.creation_date))).all()
    print(history)
    return [{"source_account": historys.account_by_id, "destination_account": historys.account_to_id, "price": historys.balance, "date": historys.creation_date, "motif": historys.motif} for historys in history ] 

@routerTransactions.post("/transactions")
def transactions(body: CreateTransactions,  user: dict = Depends(get_user), session = Depends(get_session)):
    if user["id"] is None:
        return {"error": "User not found"}
    
    if body.account_to_id is None:
        return {"error": "Account not found"}
    
    
    user_account_sender = session.exec(select(Account).where(Account.id == body.account_by_id)).first()
    user_account_receiver = session.exec(select(Account).where(Account.id == body.account_to_id)).first()

    if user_account_sender.user_id != user_account_receiver.user_id:
        print("sender", user_account_sender.user_id, "receiver", user_account_receiver.user_id)
        return {"error": "Vous ne pouvez pas faire de virement. Les deux comptes utilisateurs doivent être les mêmes"}
    if user_account_sender.user_id != user["id"]:
        return {"error": "Vous ne pouvez pas créer de transaction avec un compte qui ne vous appartient pas"}


    accountId_receiver = session.exec(select(Account).where(Account.id == body.account_to_id)).first()
    account_sender = session.exec(select(Account).where(Account.id == body.account_by_id)).first()

    if body.balance <= 0:
        return {"error": "Bah nan dcp mets de l'argent sale radin"}
    
    if account_sender.balance <= body.balance:
        return {"error": "T'es pauvre ahahahahah"}
    
    
    account_sender.balance -= body.balance
    transaction = Transactions(account_by_id = body.account_by_id, account_to_id=body.account_to_id, balance= body.balance, motif= body.motif, is_cancelled = False, is_pending= True, is_confirmed=False)
    session.add(account_sender)
    session.add(transaction)
    session.commit()
    session.refresh(transaction, account_sender)
    ceiling_account(accountId_receiver, body.balance, session)
    return transaction

    

@routerTransactions.post("/cancel_transaction") 
def cancel_transaction(transaction_id: int, user: dict = Depends(get_user), session = Depends(get_session)):
    if user["id"] is None:
        return {"error": "User not found"}
    
    transaction = session.exec(select(Transactions).where(Transactions.id == transaction_id)).first()
    account_in_transaction = session.exec(select(Account).where(Account.id == transaction.account_by_id)).first()

    if account_in_transaction.user_id != user["id"]:
        return {"error": "Vous n'êtes pas autorisé à annuler cette transaction"}
    
    if transaction is None:
        return {"error": "Transaction not found"}
    
    if transaction.is_pending == False:
        return {"error": "Transaction déjà confirmée"}

    account_in_transaction.balance += transaction.balance
    transaction.is_chancelled = True
    transaction.is_confirmed = False
    transaction.is_pending = False
    session.add(transaction)
    session.add(account_in_transaction)
    ceiling_account(account_in_transaction, session)
    session.commit()
    session.refresh(transaction)
    return transaction


@routerTransactions.get("/view_transaction")
def view_transaction(transaction_id: int, user: dict = Depends(get_user), session = Depends(get_session)):
    if user["id"] is None:
        return {"error": "User not found"}
    transaction = session.exec(select(Transactions).where(Transactions.id == transaction_id)).first()
    account_sender = session.exec(select(Account).where(Account.id == transaction.account_by_id)).first()
    account_receiver = session.exec(select(Account).where(Account.id == transaction.account_to_id)).first()
    user_sender = account_sender.user_id
    user_receiver = account_receiver.user_id

    if transaction is None:
        return {"error": "Transaction not found"}

    if user_sender != user["id"] or user_receiver != user["id"]:
        return {"error": "You are not the sender or the receiver of this transaction"}

    return  {"source_account": transaction.account_by_id, "destination_account": transaction.account_to_id, "price": transaction.balance, "date": transaction.creation_date, "motif": transaction.motif}