import json
from dataclasses import dataclass
from typing import Generator, List, Tuple

from _typeshed import StrEnum
from kafka import KafkaConsumer

import repositories as repo


class TasksEventType(StrEnum):
    ASSIGNEE = "assigneeTaskEvent"
    COMPLETE = "completeTaskEvent"


@dataclass
class TasksMessageValueV1:
    username: str
    cost: float


@dataclass
class TasksEventMessageHeaders:
    event_type: TasksEventType


@dataclass
class TasksEvent:
    value: TasksMessageValueV1
    headers: TasksEventMessageHeaders


class UsersConsumer:
    GROUP_ID = "accounting"

    _EVENT_TYPE_HEADER_KEY = "eventType"

    _SUPPORTED_HEADERS = (_EVENT_TYPE_HEADER_KEY,)

    def __init__(
        self,
        topic_name: str,
    ) -> None:
        self._consumer = KafkaConsumer(
            topic_name,
            group_id=self.GROUP_ID,
            bootstrap_servers="localhost:9092",
        )

    def subscribe(self) -> Generator[TasksEvent, None, None]:
        for msg in self._consumer:
            yield TasksEvent(
                value=self._construct_msg_value(msg.value),
                headers=self._construct_user_event_header(msg.headers),
            )

    @staticmethod
    def _construct_msg_value(value_bytes: bytes) -> TasksMessageValueV1:
        json_value = json.loads(value_bytes)

        return TasksMessageValueV1(username=json_value["username"], cost=json_value["cost"])

    @classmethod
    def _construct_user_event_header(cls, raw_headers: List[Tuple[str, bytes]]) -> TasksEventMessageHeaders:
        _headers = {}
        for header_key, header_value in raw_headers:
            if header_key not in cls._SUPPORTED_HEADERS:
                continue

            if header_key == cls._EVENT_TYPE_HEADER_KEY:
                _headers["event_type"] = TasksEventType(header_value.decode())
            else:
                raise ValueError(f"{header_key=} wrong. cannot be here")

        return TasksEventMessageHeaders(**_headers)

    def __iter__(self) -> KafkaConsumer:
        return self._consumer


def sync_account_balance() -> None:
    consumer = UsersConsumer(topic_name="users")

    for msg in consumer.subscribe():
        if msg.headers.event_type == TasksEventType.ASSIGNEE:
            account = repo.get_account_by_username(msg.value.username)
            transaction = account.charge_off(msg.value.cost)
            repo.create_transaction(account, transaction)
            repo.save_account(account)
        elif msg.headers.event_type == TasksEventType.COMPLETE:
            account = repo.get_account_by_username(msg.value.username)
            transaction = account.deposit(msg.value.cost)
            repo.create_transaction(account, transaction)
            repo.save_account(account)

        continue
