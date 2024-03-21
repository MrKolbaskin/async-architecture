from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID


class TransactionType(StrEnum):
    PAYMENT = "PAYMENT"
    DEPOSIT = "DEPOSIT"
    CHARGE_OFF = "CHARGE_OFF"


@dataclass
class Transaction:
    id: UUID
    cost: float
    type_: TransactionType
