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
        accountId1 = session.exec(select(Account).where(Account.id == body.account_to_id)).first()
        accountId2 = session.exec(select(Account).where(Account.id == body.account_by_id)).first()

        if body.balance <= 0:
            return {"error": "Bah nan dcp m'est de l'argent sale radin"}

        accountId1.balance += body.balance
        accountId2.balance -= body.balance
        session.add(accountId1)
        session.add(accountId2)

        transactions = Transactions(account_by_id = body.account_by_id, account_to_id=body.account_to_id, balance= body.balance, motif= "Non Merci", is_cancelled = False  )

        session.add(transactions)
        session.commit()
        session.refresh(transactions)
        session.refresh(accountId1)
        session.refresh(accountId2)
        
        return transactions, accountId1, accountId2
    else:
        return {"error": "Account Not Found"}