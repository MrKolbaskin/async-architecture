import json
from dataclasses import dataclass
from enum import Enum
from typing import Generator, List, Tuple

from kafka import KafkaConsumer

import repositories.user as user_repo


class UserEventType(Enum):
    USER_ADDED_EVENT = "CreateUserEvent"


@dataclass
class CreateUserMessageValueV1:
    username: str


@dataclass
class UserEventMessageHeaders:
    event_type: UserEventType


@dataclass
class UserEvent:
    value: CreateUserMessageValueV1
    headers: UserEventMessageHeaders


class UsersConsumer:
    GROUP_ID = "task-tracker"

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

    def subscribe(self) -> Generator[UserEvent, None, None]:
        for msg in self._consumer:
            yield UserEvent(
                value=self._construct_msg_value(msg.value),
                headers=self._construct_user_event_header(msg.headers),
            )

    @staticmethod
    def _construct_msg_value(value_bytes: bytes) -> CreateUserMessageValueV1:
        json_value = json.loads(value_bytes)

        return CreateUserMessageValueV1(username=json_value["username"])

    @classmethod
    def _construct_user_event_header(cls, raw_headers: List[Tuple[str, bytes]]) -> UserEventMessageHeaders:
        _headers = {}
        for header_key, header_value in raw_headers:
            if header_key not in cls._SUPPORTED_HEADERS:
                continue

            if header_key == cls._EVENT_TYPE_HEADER_KEY:
                _headers["event_type"] = UserEventType(header_value.decode())
            else:
                raise ValueError(f"{header_key=} wrong. cannot be here")

        return UserEventMessageHeaders(**_headers)

    def __iter__(self) -> KafkaConsumer:
        return self._consumer


def sync_users() -> None:
    consumer = UsersConsumer(topic_name="users")

    for msg in consumer.subscribe():
        if msg.headers.event_type != UserEventType.USER_ADDED_EVENT:
            continue

        user_repo.create_user(msg.value.username)
