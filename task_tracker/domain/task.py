import random
import uuid
from dataclasses import dataclass
from enum import StrEnum
from typing import List

from .user import User


class ChangeStatusError(Exception):
    pass


class TaskStatus(StrEnum):
    TODO = "TODO"
    DONE = "DONE"


class CompleteTaskError(Exception):
    pass


@dataclass
class Task:
    id: uuid.UUID
    description: str
    status: TaskStatus
    assignee: User
    assignee_cost: float
    complete_cost: float

    MINIMAL_ASSIGNEE_COST: int = 10
    MAXIMUM_ASSIGNEE_COST: int = 20
    MINIMAL_COMPLETE_COST: int = 20
    MAXIMUM_COMPLETE_COST: int = 40

    @classmethod
    def create_new(cls, assignee: User, description: str = "", status: TaskStatus = TaskStatus.TODO) -> "Task":
        return cls(
            id=uuid.uuid4(),
            assignee=assignee,
            description=description,
            status=status,
            assignee_cost=random.randint(cls.MINIMAL_ASSIGNEE_COST, cls.MAXIMUM_ASSIGNEE_COST),
            complete_cost=random.randint(cls.MINIMAL_COMPLETE_COST, cls.MAXIMUM_COMPLETE_COST),
        )

    def complete(self, current_user: User) -> None:
        if self.assignee != current_user:
            raise CompleteTaskError("only assignee user can complete task")

        self.status = TaskStatus.DONE

    def reassignee(self, users: List[User]) -> None:
        self.assignee = random.choice(users)
