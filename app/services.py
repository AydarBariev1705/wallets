from uuid import UUID
from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import WalletModel

class WalletService:
    @staticmethod
    async def validate_wallet(wallet_id: UUID, db: AsyncSession) -> WalletModel:
        """Проверяет, существует ли кошелек."""
        wallet = await db.get(WalletModel, wallet_id)
        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Wallet not found",
                )
        return wallet

    @staticmethod
    async def validate_amount(amount: Decimal):
        """Проверяет, что сумма операции больше 0."""
        if amount <= Decimal('0.0'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Amount must be greater than 0",
                )

    @staticmethod
    async def validate_withdrawal(wallet: WalletModel, amount: Decimal):
        """Проверяет, достаточно ли средств для вывода."""
        if wallet.balance < amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Insufficient funds",
                )