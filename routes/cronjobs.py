from fastapi import Depends
from .models import Transactions
from .models import Account
from .config import *
from datetime import datetime
from .dependencies import ceiling_account

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
    return {"message": "Aucune transaction en attente"}
       
       
def surplus(transaction: Transactions, surplus: int, account_receiver: Account, account_sender: Account, session = Depends(get_session)):
    user = account_receiver.user
    principal_account = session.exec(select(Account).where(Account.user_id == user.id, Account.is_principal == True)).first()
    if principal_account:
        principal_account.balance += surplus
        session.add(principal_account)
        session.commit()
        session.refresh(principal_account)
        return {"transaction": transaction, "message": "Surplus ajouté au compte principal"}
    else:
        return {"transaction": transaction, "message": "Compte principal non trouvé"}
