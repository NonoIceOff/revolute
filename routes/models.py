from sqlmodel import Field, Relationship, SQLModel
from datetime import date, datetime


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    firstname: str = Field(min_length=1, max_length=255)
    lastname: str = Field(min_length=1, max_length=255)
    email: str = Field(min_length=1, unique=True, max_length=255)
    password: str = Field(min_length=1, max_length=255)

class AccountTypes(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(min_length=1, max_length=255)

class Account(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    type_id: int = Field(foreign_key="accounttypes.id")
    name: str = Field(min_length=1, max_length=255)
    iban: str = Field(max_length=255)
    balance: float = Field(default=0)
    is_principal: bool = Field(default=False)
    is_closed: bool = Field(default=False)
    creation_date: date = Field(default=date.today())


class Transactions(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    account_by_id: int = Field(default=None, foreign_key="account.id")
    account_to_id: int = Field(default=None, foreign_key="account.id")
    balance: float = Field(default=0)
    motif: str | None = Field(default=None)
    creation_date: datetime = Field(default=datetime.now())
    is_chancelled: bool = Field(default=False)
    is_pending: bool = Field(default=False)
    is_confirmed: bool = Field(default=False)

class Virements(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    account_by_id: int = Field(default=None, foreign_key="account.id")
    account_to_id: int = Field(default=None, foreign_key="account.id")
    balance: float = Field(default=0)
    motif: str | None = Field(default=None)
    creation_date: datetime = Field(default=datetime.now())
    is_chancelled: bool = Field(default=False)
    is_pending: bool = Field(default=False)
    is_confirmed: bool = Field(default=False)

class Deposits(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    account: int = Field(default=None, foreign_key="account.id")
    earn: float = Field(default=0)
    motif: str = Field(max_length=255)
    creation_date: datetime = Field(default=datetime.now())

class Beneficiary(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    user_account_beneficiary: int = Field(default=None, foreign_key="account.id")
    creation_date: datetime = Field(default=datetime.now())

class Prelevements(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    amount: float = Field(default=0)
    frequency: int = Field(default=0)
    account_to_id: int = Field(default=None, foreign_key="account.id")
    creation_date: datetime = Field(default=datetime.now())