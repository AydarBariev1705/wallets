from uuid import UUID
from decimal import Decimal
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, condecimal, ConfigDict

from app.enums import OperationType

class WalletBase(BaseModel):
    id: UUID
    balance: condecimal(gt=Decimal("0.0"))  # Ограничение: баланс должен быть больше 0

    model_config = ConfigDict(
        from_attributes=True,
        )

class WalletCreate(BaseModel):
    balance: Optional[condecimal(ge=Decimal("0.0"))] = Decimal("0.0")  # Баланс может быть равен или больше 0


class DepositBase(BaseModel):
    id: int
    amount: condecimal(gt=Decimal("0.0"))  # Ограничение: сумма депозита должна быть больше 0
    wallet_id: UUID
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        )

class WithdrawBase(BaseModel):
    id: int
    amount: condecimal(gt=Decimal("0.0"))  # Ограничение: сумма вывода должна быть больше 0
    wallet_id: UUID
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        )

class OperationBase(BaseModel):
    amount: condecimal(gt=Decimal("0.0"))  # Сумма должна быть больше 0

    model_config = ConfigDict(
        from_attributes=True,
        )

class OperationCreate(OperationBase):
    operation_type: OperationType

class OperationList(OperationBase):
    id: int
    wallet_id: UUID
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        )
    
class WalletResponse(BaseModel):
    id: UUID
    balance: Decimal
    deposits: List[OperationList] = []
    withdraws: List[OperationList] = []

    model_config = ConfigDict(
        from_attributes=True,
        )