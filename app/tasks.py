import asyncio
from uuid import UUID
from decimal import Decimal
from contextlib import asynccontextmanager

from app.repo import WalletRepo
from app.database import get_db
from app.enums import OperationType
from app.celery_app import celery_app

# Асинхронный контекстный менеджер для работы с сессией
@asynccontextmanager
async def get_db_session():
    async for session in get_db():
        yield session

@celery_app.task
def perform_operation(wallet_id: str, operation_type: str, amount: Decimal):
    operation_type_enum = OperationType(operation_type)
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        # Если цикла событий нет, создаем новый
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # Выполняем асинхронный код в созданном цикле событий
    result = loop.run_until_complete(
        _perform_operation_async(
            wallet_id=wallet_id,
            operation_type=operation_type_enum, 
            amount=amount,
            ),
            )
    return result

async def _perform_operation_async(wallet_id: str, operation_type: OperationType, amount: Decimal):
    async with get_db_session() as db:
        wallet_repo = WalletRepo(db)
        
        if operation_type == OperationType.DEPOSIT:
            deposit = await wallet_repo.create_deposit(
                wallet_id=UUID(wallet_id), 
                amount=amount,
                )
            return {
                "id": deposit.id,
                "operation_type": operation_type.value,
                "amount": float(deposit.amount),
                "wallet_id": str(deposit.wallet_id),
                "created_at": deposit.created_at.isoformat(),
            }

        elif operation_type == OperationType.WITHDRAW:
            withdraw = await wallet_repo.create_withdraw(
                wallet_id=UUID(wallet_id), 
                amount=amount,
                )
            return {
                "id": withdraw.id,
                "operation_type": operation_type.value,
                "amount": float(withdraw.amount),
                "wallet_id": str(withdraw.wallet_id),
                "created_at": withdraw.created_at.isoformat(),
            }