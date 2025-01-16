import asyncio
from app.celery_app import celery_app
from app.models import WalletModel, DepositModel, WithdrawModel
from app.database import get_db  # Используем get_db из database.py
from decimal import Decimal
from uuid import UUID
from app.enums import OperationType
from contextlib import asynccontextmanager

# Асинхронный контекстный менеджер для работы с сессией
@asynccontextmanager
async def get_db_session():
    async for session in get_db():
        yield session

@celery_app.task
def perform_operation(wallet_id: str, operation_type: str, amount: Decimal):
    # Преобразуем operation_type в OperationType
    try:
        operation_type_enum = OperationType(operation_type)  # Преобразуем строку в Enum
    except ValueError:
        raise ValueError(f"Invalid operation type: {operation_type}. Must be one of {[op.value for op in OperationType]}")
    # Используем asyncio.run для выполнения асинхронного кода
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        # Если цикла событий нет, создаем новый
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # Выполняем асинхронный код в созданном цикле событий
    result = loop.run_until_complete(_perform_operation_async(wallet_id, operation_type_enum, amount))
    return result

async def _perform_operation_async(wallet_id: str, operation_type: OperationType, amount: Decimal):
    # Используем get_db_session для получения сессии
    async with get_db_session() as db:
        # Ищем кошелек по ID
        wallet = await db.get(WalletModel, UUID(wallet_id))
        if not wallet:
            raise ValueError("Wallet not found")

        # Обрабатываем операцию в зависимости от типа
        if operation_type == OperationType.DEPOSIT:
            # Создаем депозит
            deposit = DepositModel(amount=amount, wallet_id=UUID(wallet_id))
            db.add(deposit)
            wallet.balance += amount  # Увеличиваем баланс кошелька

        elif operation_type == OperationType.WITHDRAW:
            # Создаем вывод
            withdraw = WithdrawModel(amount=amount, wallet_id=UUID(wallet_id))
            db.add(withdraw)
            wallet.balance -= amount  # Уменьшаем баланс кошелька

        # Сохраняем изменения в базе данных
        await db.commit()
        await db.refresh(wallet)

        # Возвращаем информацию о выполненной операции
        if operation_type == OperationType.DEPOSIT:
            return {
                "id": deposit.id,
                "operation_type": operation_type.value,  
                "amount": float(deposit.amount),  
                "wallet_id": str(deposit.wallet_id),
                "created_at": deposit.created_at.isoformat(),
            }
        else:
            return {
                "id": withdraw.id,
                "operation_type": operation_type.value,  
                "amount": float(withdraw.amount),  
                "wallet_id": str(withdraw.wallet_id),
                "created_at": withdraw.created_at.isoformat(),
            }