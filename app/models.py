from uuid import uuid4
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, ForeignKey, Numeric, UUID, DateTime

from app.database import Base

class WalletModel(Base):
    __tablename__ = "wallets"
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid4,
        )
    balance = Column(
        Numeric(10, 2), nullable=False, default=0.0,
        )
    deposits = relationship(
        "DepositModel", back_populates="wallet", cascade="all, delete-orphan",
        )
    withdraws = relationship(
        "WithdrawModel", back_populates="wallet", cascade="all, delete-orphan",
        )

    def __init__(self, balance=0.0):
        self.id = uuid4()
        self.balance = max(balance, 0.0)  # Гарантирует, что баланс всегда >= 0
        self.deposits = []
        self.withdraws = []

    def __repr__(self):
        return f"<Wallet(id={self.id}, balance={self.balance})>"

class DepositModel(Base):
    __tablename__ = "deposits"
    id = Column(
        Integer, primary_key=True, autoincrement=True,
        )
    amount = Column(
        Numeric(10, 2), nullable=False,
        )
    wallet_id = Column(
        UUID(as_uuid=True), ForeignKey("wallets.id"), nullable=False,
        )
    created_at = Column(
        DateTime, default=datetime.utcnow, nullable=False,
        )
    wallet = relationship(
        "WalletModel", back_populates="deposits",
        )

    def __init__(self, amount, wallet_id):
        self.amount = amount
        self.wallet_id = wallet_id

    def __repr__(self):
        return f"<Deposit(id={self.id}, amount={self.amount}, wallet_id={self.wallet_id})>"

class WithdrawModel(Base):
    __tablename__ = "withdraws"
    id = Column(
        Integer, primary_key=True, autoincrement=True,
        )
    amount = Column(
        Numeric(10, 2), nullable=False,
        )
    wallet_id = Column(
        UUID(as_uuid=True), ForeignKey("wallets.id"), nullable=False,
        )
    created_at = Column(
        DateTime, default=datetime.utcnow, nullable=False,
        )
    wallet = relationship(
        "WalletModel", back_populates="withdraws",
        )

    def __init__(self, amount, wallet_id):
        self.amount = amount
        self.wallet_id = wallet_id

    def __repr__(self):
        return f"<Withdraw(id={self.id}, amount={self.amount}, wallet_id={self.wallet_id})>"