from uuid import UUID
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status


from app.repo import WalletRepo
from app.database import get_db
from app.enums import OperationType
from app.services import WalletService
from app.tasks import perform_operation
from app.schemas import OperationCreate, WalletCreate, WalletResponse


router = APIRouter(
    prefix="/api/v1/wallets",
    tags=["wallets"],
    )
@router.post("/", response_model=WalletResponse)
async def create_wallet(wallet_create: WalletCreate, db: AsyncSession = Depends(get_db)):
    wallet_repo = WalletRepo(db)
    new_wallet = await wallet_repo.create_wallet(
        balance=wallet_create.balance or Decimal("0.0"),
        )
    new_wallet = await wallet_repo.get_wallet_by_id(
        wallet_id=new_wallet.id,
        )
    return new_wallet
 

@router.get("/{wallet_id}", response_model=WalletResponse)
async def get_wallet(wallet_id: UUID, db: AsyncSession = Depends(get_db)):
    wallet_repo = WalletRepo(db)
    wallet = await wallet_repo.get_wallet_by_id(
        wallet_id=wallet_id,
        )
    
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Wallet not found",
            )
    
    return wallet

    
@router.post("/{wallet_id}/operation")
async def create_operation(wallet_id: UUID, transaction_create: OperationCreate, db: AsyncSession = Depends(get_db)):
    wallet = await WalletService.validate_wallet(
        wallet_id=wallet_id, 
        db=db,
        )
    await WalletService.validate_amount(
        amount=transaction_create.amount,
        )
    if transaction_create.operation_type == OperationType.WITHDRAW:
        await WalletService.validate_withdrawal(
            wallet=wallet, 
            amount=transaction_create.amount,
            )

    # Отправляем задачу в Celery
    task = perform_operation.delay(
        wallet_id=str(wallet_id),
        operation_type=transaction_create.operation_type.value,
        amount=transaction_create.amount,
    )
    return {"task_id": task.id}