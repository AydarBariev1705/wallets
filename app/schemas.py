from pydantic import BaseModel, condecimal, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional
from decimal import Decimal
from app.enums import OperationType
from typing import List

class WalletBase(BaseModel):
    id: UUID
    balance: condecimal(gt=Decimal('0.0'))  # Ограничение: баланс должен быть больше 0

    model_config = ConfigDict(from_attributes=True)

class WalletCreate(BaseModel):
    balance: Optional[condecimal(ge=Decimal('0.0'))] = Decimal('0.0')  # Баланс может быть равен или больше 0


class DepositBase(BaseModel):
    id: int
    amount: condecimal(gt=Decimal('0.0'))  # Ограничение: сумма депозита должна быть больше 0
    wallet_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class WithdrawBase(BaseModel):
    id: int
    amount: condecimal(gt=Decimal('0.0'))  # Ограничение: сумма вывода должна быть больше 0
    wallet_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TransactionBase(BaseModel):
    amount: condecimal(gt=Decimal('0.0'))  # Сумма должна быть больше 0

    model_config = ConfigDict(from_attributes=True)

class TransactionCreate(TransactionBase):
    operation_type: OperationType

class TransactionList(TransactionBase):
    id: int
    wallet_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TransactionResponse(TransactionList):
    operation_type: OperationType

    model_config = ConfigDict(from_attributes=True)

class WalletResponse(BaseModel):
    id: UUID
    balance: Decimal
    deposits: List[TransactionList] = []
    withdraws: List[TransactionList] = []

    model_config = ConfigDict(from_attributes=True)