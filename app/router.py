from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import WalletModel, DepositModel, WithdrawModel
from app.schemas import TransactionCreate, TransactionResponse, WalletCreate, WalletResponse

from sqlalchemy.orm import selectinload
from decimal import Decimal
from sqlalchemy import select
from app.enums import OperationType
from app.tasks import perform_operation


router = APIRouter(
    prefix="/api/v1/wallets",
    tags=["wallets"],
    )
@router.post("/", response_model=WalletResponse)
async def create_wallet(wallet_create: WalletCreate, db: AsyncSession = Depends(get_db)):
    new_wallet = WalletModel(balance=wallet_create.balance or Decimal('0.0'))
    new_wallet.deposits = []
    new_wallet.withdraws = []

    db.add(new_wallet)
    await db.commit()
    await db.refresh(new_wallet)

    # Явно загружаем связанные данные
    result = await db.execute(
        select(WalletModel)
        .options(selectinload(WalletModel.deposits), selectinload(WalletModel.withdraws))
        .where(WalletModel.id == new_wallet.id)
    )
    new_wallet = result.scalars().first()

    return new_wallet
 

@router.get("/{wallet_id}", response_model=WalletResponse)
async def get_wallet(wallet_id: UUID, db: AsyncSession = Depends(get_db)):
    # Ищем кошелек по ID с загрузкой связанных объектов
    query = await db.execute(
        select(WalletModel)
        .options(selectinload(WalletModel.deposits))
        .options(selectinload(WalletModel.withdraws))
        .where(WalletModel.id == wallet_id)
    )
    
    wallet = query.scalar_one_or_none()
    
    if not wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")

    return wallet

@router.post("/{wallet_id}/operation2", response_model=TransactionResponse)
async def create_operation2(wallet_id: UUID, transaction_create: TransactionCreate, db: AsyncSession = Depends(get_db)):
    # Ищем кошелек по ID
    wallet = await db.get(WalletModel, wallet_id)
    if not wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")

    # Проверяем, что сумма операции больше 0
    if transaction_create.amount <= Decimal('0.0'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Amount must be greater than 0")

    # Обрабатываем операцию в зависимости от типа
    if transaction_create.operation_type == OperationType.DEPOSIT:
        # Создаем депозит
        deposit = DepositModel(amount=transaction_create.amount, wallet_id=wallet_id)
        db.add(deposit)
        wallet.balance += transaction_create.amount  # Увеличиваем баланс кошелька

    elif transaction_create.operation_type == OperationType.WITHDRAW:
        # Проверяем, достаточно ли средств на кошельке для вывода
        if wallet.balance < transaction_create.amount:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient funds")

        # Создаем вывод
        withdraw = WithdrawModel(amount=transaction_create.amount, wallet_id=wallet_id)
        db.add(withdraw)
        wallet.balance -= transaction_create.amount  # Уменьшаем баланс кошелька

    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid operation type")

    # Сохраняем изменения в базе данных
    await db.commit()
    await db.refresh(wallet)

    # Возвращаем информацию о выполненной операции
    if transaction_create.operation_type == OperationType.DEPOSIT:
        return TransactionResponse(
            id=deposit.id,
            operation_type=OperationType.DEPOSIT,
            amount=deposit.amount,
            wallet_id=deposit.wallet_id,
            created_at=deposit.created_at
        )
    else:
        return TransactionResponse(
            id=withdraw.id,
            operation_type=OperationType.WITHDRAW,
            amount=withdraw.amount,
            wallet_id=withdraw.wallet_id,
            created_at=withdraw.created_at
        )
    
@router.post("/{wallet_id}/operation")
async def create_operation(wallet_id: UUID, transaction_create: TransactionCreate, db: AsyncSession = Depends(get_db)):
        # Ищем кошелек по ID
    wallet = await db.get(WalletModel, wallet_id)
    if not wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")

    # Проверяем, что сумма операции больше 0
    if transaction_create.amount <= Decimal('0.0'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Amount must be greater than 0")
    
    if transaction_create.operation_type == OperationType.WITHDRAW:
        if wallet.balance < transaction_create.amount:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient funds")

    # Отправляем задачу в Celery
    task = perform_operation.delay(
        wallet_id=str(wallet_id),
        operation_type=transaction_create.operation_type.value,
        amount=transaction_create.amount,
    )

    # Возвращаем ID задачи и статус
    return {"task_id": task.id, "status": "Task submitted"}