from uuid import UUID
from decimal import Decimal
from sqlalchemy import select
from abc import ABC, abstractmethod
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession


from app.models import WalletModel, DepositModel, WithdrawModel

class WalletRepoABC(ABC):
    @abstractmethod
    async def create_wallet(self, balance: Decimal = Decimal('0.0')) -> WalletModel:
        pass

    @abstractmethod
    async def get_wallet_by_id(self, wallet_id: UUID, load_deposits: bool = True, load_withdraws: bool = True) -> WalletModel:
        pass

    @abstractmethod
    async def get_wallet(self, wallet_id: UUID) -> WalletModel:
        pass

    @abstractmethod
    async def create_deposit(self, wallet_id: UUID, amount: Decimal) -> DepositModel:
        pass

    @abstractmethod
    async def create_withdraw(self, wallet_id: UUID, amount: Decimal) -> WithdrawModel:
        pass


class WalletRepo(WalletRepoABC):
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_wallet(self, balance: Decimal = Decimal('0.0')) -> WalletModel:
        """Создает новый кошелек."""
        new_wallet = WalletModel(balance=balance)
        new_wallet.deposits = []
        new_wallet.withdraws = []
        self.db.add(new_wallet)
        await self.db.commit()
        await self.db.refresh(new_wallet)
        return new_wallet
    
    async def get_wallet_by_id(self, wallet_id: UUID, load_deposits: bool = True, load_withdraws: bool = True) -> WalletModel:
        """Получает кошелек по ID с возможностью загрузки связанных данных."""
        query = select(WalletModel).where(WalletModel.id == wallet_id)
        
        if load_deposits:
            query = query.options(selectinload(WalletModel.deposits))
        if load_withdraws:
            query = query.options(selectinload(WalletModel.withdraws))
        
        result = await self.db.execute(query)
        wallet = result.scalar_one_or_none()
        return wallet

    async def get_wallet(self, wallet_id: UUID) -> WalletModel:
        wallet = await self.db.get(WalletModel, wallet_id)
        if not wallet:
            raise ValueError("Wallet not found")
        return wallet

    async def create_deposit(self, wallet_id: UUID, amount: Decimal) -> DepositModel:
        wallet = await self.get_wallet(wallet_id)
        deposit = DepositModel(
            amount=amount, 
            wallet_id=wallet_id,
            )
        self.db.add(deposit)
        wallet.balance += amount
        await self.db.commit()
        await self.db.refresh(wallet)
        return deposit

    async def create_withdraw(self, wallet_id: UUID, amount: Decimal) -> WithdrawModel:
        wallet = await self.get_wallet(wallet_id)
        withdraw = WithdrawModel(
            amount=amount, 
            wallet_id=wallet_id,
            )
        self.db.add(withdraw)
        wallet.balance -= amount
        await self.db.commit()
        await self.db.refresh(wallet)
        return withdraw