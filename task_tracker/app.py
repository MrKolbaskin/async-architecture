from threading import Thread
from typing import Any, Dict

import requests
from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel

import repositories.task as task_repo
import repositories.user as user_repo
from jobs import sync_users

sync_users_job = Thread(target=sync_users, name="sync_users_job")
sync_users_job.start()

app = FastAPI()


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

    task_repo.create_task(body.description, user)
    return {}


@app.put("/tasks/{task_id}/complete")
async def complete_task(task_id: int, token_payload: Dict[str, Any] = Depends(verify_token)):
    user = user_repo.get_user_by_username(token_payload["clientId"])
    task = task_repo.get_task_by_id(task_id)

    task.complete(user)
    task_repo.save(task)

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

    return {}
