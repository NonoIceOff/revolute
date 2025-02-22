from datetime import date, datetime
from fastapi import APIRouter, Depends
from sqlmodel import desc
from .schemas import CreateTransactions
from .models import Transactions, Account
from .config import *
from .dependencies import ceiling_account
from fastapi import HTTPException
from sqlmodel import desc
from apscheduler.schedulers.background import BackgroundScheduler


    #🥝🥝                                      🥝🥝         
    #🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝
    #🥝🥝🥝🥝👁️🥝🥝🥝🥝🥝🥝🥝🥝🥝👁️🥝🥝🥝🥝
    #🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝
    #🥝🥝🥝🥝🥝🥝🦷🦷🦷🦷🦷🦷🦷🥝🥝🥝🥝🥝🥝
    #🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝


routerTransactions = APIRouter()
is_finish = False
scheduler = BackgroundScheduler()
scheduler.start()

@routerTransactions.on_event("shutdown")
def on_shutdown():
    scheduler.shutdown()


## Transactions pour tout l'utilisateur
@routerTransactions.post("/transactions/history", tags=["transactions"])
def historyTransactions(user: dict = Depends(get_user), session: Session = Depends(get_session)):
    user_id = user["id"]
    
    # Récupérer tous les comptes de l'utilisateur
    accounts = session.exec(select(Account).where(Account.user_id == user_id)).all()
    account_ids = [account.id for account in accounts]
    
    # Récupérer toutes les transactions où l'utilisateur est impliqué
    history = session.exec(
        select(Transactions).where(
            (Transactions.account_by_id.in_(account_ids)) | (Transactions.account_to_id.in_(account_ids))
        ).order_by(desc(Transactions.creation_date))
    ).all()
    
    if not history:
        raise HTTPException(status_code=404, detail="No transactions found for this user")

    transactions_list = []
    for transaction in history:
        # Ajouter la transaction comme perte
        transactions_list.append({
            "source_account": transaction.account_by_id,
            "destination_account": transaction.account_to_id,
            "source_account_name": transaction.account_by.name,
            "source_destination_name": transaction.account_to.name,
            "price": -transaction.balance,
            "date": transaction.creation_date,
            "motif": transaction.motif
        })
        # Ajouter la transaction comme gain
        transactions_list.append({
            "source_account": transaction.account_to_id,
            "destination_account": transaction.account_by_id,
            "source_account_name": transaction.account_to.name,
            "destination_account_name": transaction.account_by.name,
            "price": transaction.balance,
            "date": transaction.creation_date,
            "motif": transaction.motif
        })

    return transactions_list

# Transactions d'un compte bancaire
@routerTransactions.get("/account/transactions", tags=["transactions"])
def account_transactions(account_id: int, user: dict = Depends(get_user), session: Session = Depends(get_session)):
    transactions = session.exec(
        select(Transactions).where(
            (Transactions.account_by_id == account_id) | (Transactions.account_to_id == account_id)
        ).order_by(desc(Transactions.creation_date))
    ).all()

    if not transactions:
        raise HTTPException(status_code=404, detail="No transactions found for this account")

    return [
        {
            "id": transaction.id,
            "source_account": transaction.account_by_id,
            "destination_account": transaction.account_to_id,
            "price": transaction.balance,
            "date": transaction.creation_date,
            "motif": transaction.motif
        }
        for transaction in transactions
    ]

@routerTransactions.post("/transactions", tags=["transactions"])
def transactions(body: CreateTransactions,  user: dict = Depends(get_user), session = Depends(get_session)):
    if body.account_to_id is None:
         raise HTTPException(status_code=404, detail="Account not found")
    
    user_account_sender = session.exec(select(Account).where(Account.id == body.account_by_id)).first()
    user_account_receiver = session.exec(select(Account).where(Account.id == body.account_to_id)).first()

    if user_account_sender is None:
        raise HTTPException(status_code=404, detail="Account sender not found")
    if user_account_receiver is None:
        raise HTTPException(status_code=404, detail="Account receiver not found")

    if body.account_to_id == body.account_by_id:
        raise HTTPException(status_code=404, detail="You cannot make a transfer. The two bank accounts are the same")

    if user_account_sender.user_id != user_account_receiver.user_id:
        raise HTTPException(status_code=404, detail="You cannot make a transfer. The two user accounts must be the same")
    if user_account_sender.user_id != user["id"]:
        raise HTTPException(status_code=404, detail="You cannot create a transaction with an account that does not belong to you")


    accountId_receiver = session.exec(select(Account).where(Account.id == body.account_to_id)).first()
    account_sender = session.exec(select(Account).where(Account.id == body.account_by_id)).first()

    if body.balance <= 0:
        raise HTTPException(status_code=404, detail="You cannot make a transfer with a negative amount")
    
    if account_sender.balance <= body.balance:
        raise HTTPException(status_code=404, detail="Insufficient balance")
    
    
    account_sender.balance -= body.balance
    transaction = Transactions(account_by_id = body.account_by_id, account_to_id=body.account_to_id, balance= body.balance, motif= body.motif, is_cancelled = False, is_pending= True, is_confirmed=False, creation_date=datetime.now())
    session.add(account_sender)
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    session.refresh(account_sender)
    ceiling_account(accountId_receiver, body.balance, session)
    print(transaction)
    return transaction
    

@routerTransactions.post("/transaction/cancel", tags=["transactions"]) 
def cancel_transaction(transaction_id: int, user: dict = Depends(get_user), session = Depends(get_session)):
    transaction = session.exec(select(Transactions).where(Transactions.id == transaction_id)).first()
    account_in_transaction = session.exec(select(Account).where(Account.id == transaction.account_by_id)).first()

    if account_in_transaction.user_id != user["id"]:
        raise HTTPException(status_code=404, detail="You're not allowed to cancel this transaction")
    
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    if transaction.is_pending == False:
        raise HTTPException(status_code=404, detail="Transaction already confirmed")

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


@routerTransactions.get("/transaction/view", tags=["transactions"])
def view_transaction(transaction_id: int, user: dict = Depends(get_user), session = Depends(get_session)):
    transaction = session.exec(select(Transactions).where(Transactions.id == transaction_id)).first()
    account_sender = session.exec(select(Account).where(Account.id == transaction.account_by_id)).first()
    account_receiver = session.exec(select(Account).where(Account.id == transaction.account_to_id)).first()
    user_sender = account_sender.user_id
    user_receiver = account_receiver.user_id

    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if user_sender != user["id"] or user_receiver != user["id"]:
        raise HTTPException(status_code=404, detail="You are not the sender or the receiver of this transaction")

    return  {"id": transaction.id, "source_account": transaction.account_by_id, "destination_account": transaction.account_to_id, "price": transaction.balance, "date": transaction.creation_date, "motif": transaction.motif}



@routerTransactions.post('/cron')
def cron_transaction(body: CreateTransactions,  user: dict = Depends(get_user), session = Depends(get_session)):
    scheduler.add_job(transactions, trigger = "interval", seconds = 5, args=[body, user, session], id="kiwi")
    return {"message": "Prélèvement Automatique Activée"}

@routerTransactions.post('/cancel_cron')
def cron_transaction_cancel():
    scheduler.remove_job("kiwi")
    return {"message": "Prélèvement Automatique Désactivée"}