import random
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
    id: int
    description: str
    status: TaskStatus
    assignee: User

    def complete(self, current_user: User) -> None:
        if self.assignee != current_user:
            raise CompleteTaskError("only assignee user can complete task")

        self.status = TaskStatus.DONE

    def reassignee(self, users: List[User]) -> None:
        self.assignee = random.choice(users)
