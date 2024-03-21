import uuid
from dataclasses import dataclass

from .transaction import Transaction, TransactionType


class DepositError(Exception):
    pass


class ChargeOffError(Exception):
    pass


class EmptyBalancePaymentError(Exception):
    pass


@dataclass
class Account:
    id: uuid.UUID
    username: str
    balance: float = 0

    def charge_off(self, amount: float) -> Transaction:
        if amount < 0:
            raise ChargeOffError("amount must be positive")
        self.balance -= amount

        return Transaction(id=uuid.uuid4(), cost=amount, type_=TransactionType.CHARGE_OFF)

    def deposit(self, amount: float) -> Transaction:
        if amount < 0:
            raise DepositError("amount must be positive")
        self.balance += amount

        return Transaction(id=uuid.uuid4(), cost=amount, type_=TransactionType.DEPOSIT)

    def payment(self) -> Transaction:
        if self.balance <= 0:
            raise EmptyBalancePaymentError("payment is not allowed with empty balance")

        payment_transaction = Transaction(id=uuid.uuid4(), cost=self.balance, type_=TransactionType.PAYMENT)
        self.balance = 0
        return payment_transaction
