from sqlmodel import Session, select 
from .models import Account, Transactions


def can_create_principal_account(user_id : int, session = Session)-> bool:
    return not session.exec(select(Account.is_principal).where(Account.user_id == user_id, Account.is_principal == True)).first()

def ceiling_account(account: Account, transaction: int, session = Session):
    if (account.is_principal == False):
        principal_account = session.exec(select(Account).where(Account.user_id == account.user_id, Account.is_principal == True)).first()
        if (account.balance + transaction > 50000):
            surplus = (account.balance + transaction) - 50000
            transaction = Transactions(account_by_id = account.id, account_to_id=principal_account.id, balance= surplus, motif= "Surplus", is_cancelled = False, is_pending= True, is_confirmed=False)
            account.balance = account.balance - surplus
            session.add(account)
            session.add(transaction)
            session.commit()
            session.refresh(transaction)
            return {"message": "T'es trop blindé, ce surplus est déplacé dans ton compte principal", "surplus": surplus}
        else:
            return {"message": "Pas de surplus"}
    return {"message": "c'est le compte principal"}
