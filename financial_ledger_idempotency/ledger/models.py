from __future__ import annotations
from typing import Optional, Literal, List
from pydantic import BaseModel, Field

AccountType = Literal["ASSET","LIABILITY","REVENUE","EXPENSE"]

class CreateAccountRequest(BaseModel):
    name: str
    type: AccountType
    currency: str = Field(min_length=3, max_length=3)

class AccountResponse(BaseModel):
    account_id: str
    name: str
    type: AccountType
    currency: str

class BalanceResponse(BaseModel):
    account_id: str
    currency: str
    balance_cents: int

class TransferRequest(BaseModel):
    from_account_id: str
    to_account_id: str
    amount_cents: int = Field(gt=0)
    currency: str = Field(min_length=3, max_length=3)
    external_ref: Optional[str] = None

class TransactionResponse(BaseModel):
    txn_id: str
    txn_type: str
    currency: str
    external_ref: Optional[str]
    entries: List[dict]
