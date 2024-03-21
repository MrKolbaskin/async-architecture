from typing import Any, Dict

import requests
from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel

import repositories as repo

app = FastAPI()


class MaxCostCompletedTaskByDay(BaseModel):
    day: str
    cost: float


class AnalyticsResponse(BaseModel):
    data: list[MaxCostCompletedTaskByDay]


def verify_token(req: Request) -> dict[str, Any]:
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


@app.get("/analytics")
async def get_analytics(token_payload: Dict[str, Any] = Depends(verify_token)):
    if not token_payload["isAdmin"]:
        raise HTTPException(status_code=403, detail="Method allowed only for administrators")

    analytics_data = repo.get_analytics()
    return AnalyticsResponse(data=[MaxCostCompletedTaskByDay(**el) for el in analytics_data])
