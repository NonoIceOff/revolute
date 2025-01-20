from fastapi import Depends
from .models import Transactions
from .models import Account
from .config import *
from datetime import datetime

def distribution():
    with Session(engine) as session:
        transaction_pending = session.exec(select(Transactions).where(Transactions.is_pending == True)).all()

        for transaction in transaction_pending:
            if (datetime.now().timestamp() - transaction.creation_date.timestamp()) >= 5:
                account = session.exec(select(Account).where(Account.id == transaction.account_to_id)).first()
                transaction.is_pending = False
                transaction.is_confirmed = True
                account.balance += transaction.balance
                session.add(account)
                session.add(transaction)
        
        session.commit()
    return {"message": "No transactions in pending"}
       