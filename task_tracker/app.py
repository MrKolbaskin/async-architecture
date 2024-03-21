import json
from enum import StrEnum
from threading import Thread
from typing import Any, Dict

import requests
from fastapi import Depends, FastAPI, HTTPException, Request
from kafka import KafkaProducer
from pydantic import BaseModel

import repositories.task as task_repo
import repositories.user as user_repo
from domain.task import Task
from jobs import sync_users

sync_users_job = Thread(target=sync_users, name="sync_users_job")
sync_users_job.start()

app = FastAPI()

TASKS_TOPIC = "tasks"
producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda m: json.dumps(m).encode("ascii"),
)


class TasksEventType(StrEnum):
    ASSIGNEE = "assigneeTaskEvent"
    COMPLETE = "completeTaskEvent"


def verify_token(req: Request) -> Dict[str, Any]:
    if "Authorization" not in req.headers.keys():
        raise HTTPException(status_code=401, detail="Unauthorized")

    token = req.headers["Authorization"]

    resp = requests.post("localhost:5000/verify", headers={"authorization": token})
    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise HTTPException(status_code=500, detail="something went wrong while verifying auth token") from e

    resp_data = resp.json()

    if not resp_data.get("success", True):
        raise HTTPException(status_code=401, detail="Unauthorized")

    return resp_data


class CreateTaskBody(BaseModel):
    description: str


@app.post("/tasks")
async def create_task(body: CreateTaskBody, token_payload: Dict[str, Any] = Depends(verify_token)):
    user = user_repo.get_user_by_username(token_payload["clientId"])

    task = Task.create_new(assignee=user, description=body.description)
    task_repo.create_task(task)

    producer.send(
        TASKS_TOPIC,
        value={"username": user.username, "cost": task.assignee_cost},
        headers=("event_type", TasksEventType.ASSIGNEE),
    )
    return {}


@app.put("/tasks/{task_id}/complete")
async def complete_task(task_id: int, token_payload: Dict[str, Any] = Depends(verify_token)):
    user = user_repo.get_user_by_username(token_payload["clientId"])
    task = task_repo.get_task_by_id(task_id)

    task.complete(user)
    task_repo.save(task)

    producer.send(
        TASKS_TOPIC,
        value={"username": user.username, "cost": task.complete_cost},
        headers=("event_type", TasksEventType.COMPLETE),
    )

    return {}


@app.post("/tasks/assignee")
async def assignee_tasks(token_payload: Dict[str, Any] = Depends(verify_token)):
    if not token_payload["isAdmin"]:
        raise HTTPException(status_code=403, detail="Method allowed only for administrators")

    tasks = task_repo.get_all_uncompleted_tasks()
    users = user_repo.get_all_users()

    for task in tasks:
        task.reassignee(users)
        task_repo.save(task)
        producer.send(
            TASKS_TOPIC,
            value={"username": task.assignee.username, "cost": task.assignee_cost},
            headers=("event_type", TasksEventType.ASSIGNEE),
        )

    return {}
