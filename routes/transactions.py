from asyncio import sleep
from fastapi import APIRouter, FastAPI, Depends
from .schemas import CreateAccount
from .schemas import CreateTransactions
from .models import Account
from .models import Transactions
from .config import *


routerTransactions = APIRouter()

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
        
        transaction = Transactions(account_by_id = body.account_by_id, account_to_id=body.account_to_id, balance= body.balance, motif= "Non Merci", is_cancelled = False  )
        session.add(transaction)
        session.commit()
        session.refresh(transaction)
        check_canceled_transaction(transaction, body.balance, accountId_receiver, accountId_sender, session)
        return transaction

        
    else:
        return {"error": "Account Not Found"}
    

    @routerTransactions.post("/history")
    def historyTransactions():
        return 

def check_canceled_transaction(transaction: Transactions, balance: int, accountId_receiver: Account, accountId_sender: Account, session = Depends(get_session)):
    sleep(5)

    if transaction.is_chancelled:
        return {"error": "Transaction annulée"}
    else:
        accountId_receiver.balance += balance
        accountId_sender.balance -= balance
        session.add(accountId_receiver)
        session.add(accountId_sender)
        session.commit()
        session.refresh(accountId_receiver)
        session.refresh(accountId_sender)

        return transaction, accountId_receiver, accountId_sender

@routerTransactions.post("/cancel_transaction")
def cancel_transaction(transaction_id: int, user: dict = Depends(get_user), session = Depends(get_session)):
    transaction = session.exec(select(Transactions).where(Transactions.id == transaction_id)).first()
    if transaction is None:
        return {"error": "Transaction not found"}
    transaction.is_chancelled = True
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return transaction