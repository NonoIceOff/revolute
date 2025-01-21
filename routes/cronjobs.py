from fastapi import Depends
from .models import Transactions, Virements
from .models import Account
from .config import *
from datetime import datetime

def distribution_transactions():
    with Session(engine) as session:
        transactions_pending = session.exec(select(Transactions).where(Transactions.is_pending == True)).all()

        for transaction in transactions_pending:
            if (datetime.now().timestamp() - transaction.creation_date.timestamp()) >= 5:
                account = session.exec(select(Account).where(Account.id == transaction.account_to_id)).first()
                transaction.is_pending = False
                transaction.is_confirmed = True
                account.balance += transaction.balance
                session.add(account)
                session.add(transaction)
        
        session.commit()
    return {"message": "No transactions in pending"}
       
def distribution_virements():
    with Session(engine) as session:
        virements_pending = session.exec(select(Virements).where(Virements.is_pending == True)).all()

        for virement in virements_pending:
            if (datetime.now().timestamp() - virement.creation_date.timestamp()) >= 5:
                account = session.exec(select(Account).where(Account.id == virement.account_to_id)).first()
                virement.is_pending = False
                virement.is_confirmed = True
                account.balance += virement.balance
                session.add(account)
                session.add(virement)
        
        session.commit()
    return {"message": "No Virements in pending"}