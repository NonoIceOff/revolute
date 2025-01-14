from sqlmodel import Session, select 
from .models import Account


def can_create_principal_account(user_id : int, session = Session)-> bool:
    return not session.exec(select(Account.is_principal).where(Account.user_id == user_id, Account.is_principal == True)).first()