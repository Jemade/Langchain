import logging
import os
import secrets
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, Literal

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

from .service import Desk

logger = logging.getLogger("freightdesk")


class Request(BaseModel):
    reference: str = Field(min_length=1, max_length=80, pattern=r"^[A-Za-z0-9_-]+$")
    shipment_id: str = Field(min_length=1, max_length=80)
    category: Literal["delay", "damage", "documents"]
    details: str = Field(min_length=10, max_length=4000)

    @field_validator("shipment_id", "details", mode="before")
    @classmethod
    def trim(cls, value):
        if not isinstance(value, str):
            raise ValueError("expected a string")
        value = value.strip()
        if not value:
            raise ValueError("blank value")
        return value


class Review(BaseModel):
    approve: bool = Field(strict=True)
    comment: str = Field(min_length=3, max_length=1000)

    @field_validator("comment")
    @classmethod
    def comment_not_blank(cls, value):
        if len(value.strip()) < 3:
            raise ValueError("add a review comment")
        return value.strip()


def create_app(directory=None, policies=None, token=None, model=None):
    if token is None:
        token = os.getenv("FREIGHTDESK_TOKEN")
    if not token or len(token) < 16 or token == "replace-with-random-token":
        raise RuntimeError("Set FREIGHTDESK_TOKEN to a random value of at least 16 characters")
    directory = Path(directory or os.getenv("FREIGHTDESK_DATA", "runtime"))
    policies = Path(policies or "data/policies")
    mode = os.getenv("FREIGHTDESK_MODE", "demo")
    if mode not in {"demo", "bedrock"}:
        raise RuntimeError("FREIGHTDESK_MODE must be demo or bedrock")
    if model is None and mode == "bedrock":
        from langchain_aws import ChatBedrockConverse

        model = ChatBedrockConverse(
            model=os.environ["BEDROCK_MODEL_ID"],
            region_name=os.environ["AWS_REGION"],
            temperature=0,
            max_tokens=700,
        )
    desk = Desk(directory, policies, model)

    @asynccontextmanager
    async def lifespan(app):
        yield
        desk.close()

    app = FastAPI(title="FreightDesk", version="0.1.0", lifespan=lifespan)
    bearer = HTTPBearer(auto_error=False)

    def auth(credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]):
        if not credentials or not secrets.compare_digest(
            credentials.credentials.encode(), token.encode()
        ):
            raise HTTPException(401, "Invalid reviewer token")

    @app.get("/health")
    def health():
        return {"status": "ok", "mode": "bedrock" if model else "demo"}

    @app.get("/api/requests", dependencies=[Depends(auth)])
    def requests():
        return desk.list()

    @app.post("/api/requests", dependencies=[Depends(auth)], status_code=201)
    def create(request: Request):
        try:
            return desk.create(request.model_dump())
        except ValueError as exc:
            raise HTTPException(409, str(exc)) from exc
        except Exception as exc:
            logger.exception("Workflow failed; retry the same reference")
            raise HTTPException(503, "Workflow failed; retry the same reference") from exc

    @app.get("/api/requests/{run_id}", dependencies=[Depends(auth)])
    def get(run_id: str):
        try:
            return desk.get(run_id)
        except KeyError as exc:
            raise HTTPException(404, "Request not found") from exc

    @app.post("/api/requests/{run_id}/review", dependencies=[Depends(auth)])
    def review(run_id: str, review: Review):
        try:
            return desk.review(run_id, review.model_dump())
        except KeyError as exc:
            raise HTTPException(404, "Request not found") from exc
        except ValueError as exc:
            raise HTTPException(409, str(exc)) from exc

    @app.get("/api/requests/{run_id}/export", dependencies=[Depends(auth)])
    def export(run_id: str):
        current = get(run_id)
        if current["status"] != "approved":
            raise HTTPException(409, "Approve the draft before export")
        return {
            "shipment_id": current["request"]["shipment_id"],
            "draft": current["draft"],
            "sources": [e["source"] for e in current["evidence"]],
            "review": current["decision"],
        }

    if Path("frontend/dist").exists():
        app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")
    return app
