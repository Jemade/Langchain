from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from langchain_core.language_models.fake_chat_models import FakeListChatModel

from freightdesk.api import create_app
from freightdesk.service import Desk

POLICIES = Path("data/policies")
TOKEN = "local-test-reviewer-token"
REQUEST = {
    "reference": "EXC-001",
    "shipment_id": "HRE-1042",
    "category": "delay",
    "details": "Carrier reports a delay. Delivery time has not been confirmed.",
}


def test_checkpoint_survives_restart_and_requires_review(tmp_path):
    desk = Desk(tmp_path, POLICIES)
    run = desk.create(REQUEST)
    assert run["status"] == "awaiting_review"
    assert run["evidence"][0]["source"] == "delay.md"
    assert desk.create(REQUEST)["id"] == run["id"]
    desk.close()
    desk = Desk(tmp_path, POLICIES)
    result = desk.review(run["id"], {"approve": True, "comment": "Carrier facts checked"})
    assert result["status"] == "approved"
    assert [e["node"] for e in result["trace"]] == ["retrieve", "draft", "review"]
    with pytest.raises(ValueError, match="not awaiting"):
        desk.review(run["id"], {"approve": False, "comment": "Repeated decision"})
    desk.close()


def test_reference_conflict_and_rejection(tmp_path):
    desk = Desk(tmp_path, POLICIES)
    run = desk.create(REQUEST)
    with pytest.raises(ValueError, match="different request"):
        desk.create({**REQUEST, "details": "A different carrier message arrived."})
    assert (
        desk.review(run["id"], {"approve": False, "comment": "Need confirmed ETA"})["status"]
        == "rejected"
    )
    desk.close()


def test_missing_policy_blocks_approval(tmp_path):
    empty = tmp_path / "policies"
    empty.mkdir()
    desk = Desk(tmp_path, empty)
    run = desk.create(REQUEST)
    assert run["status"] == "needs_information"
    with pytest.raises(ValueError):
        desk.review(run["id"], {"approve": True, "comment": "No evidence"})
    desk.close()


def test_model_is_used_but_cannot_bypass_review(tmp_path):
    model = FakeListChatModel(responses=["Request the last verified location from the carrier."])
    desk = Desk(tmp_path, POLICIES, model)
    run = desk.create(REQUEST)
    assert run["mode"] == "bedrock"
    assert run["draft"].startswith("Request the last verified")
    assert run["status"] == "awaiting_review"
    desk.close()


def test_api_auth_validation_and_export(tmp_path):
    with TestClient(create_app(tmp_path, token=TOKEN)) as client:
        assert client.get("/health").status_code == 200
        assert client.get("/api/requests").status_code == 401
        headers = {"Authorization": "Bearer " + TOKEN}
        assert (
            client.post(
                "/api/requests", headers=headers, json={**REQUEST, "category": "unknown"}
            ).status_code
            == 422
        )
        assert (
            client.post(
                "/api/requests", headers=headers, json={**REQUEST, "details": " " * 12}
            ).status_code
            == 422
        )
        run = client.post("/api/requests", headers=headers, json=REQUEST).json()
        assert client.get(f"/api/requests/{run['id']}/export", headers=headers).status_code == 409
        path = f"/api/requests/{run['id']}/review"
        assert (
            client.post(
                path, headers=headers, json={"approve": "true", "comment": "   "}
            ).status_code
            == 422
        )
        assert (
            client.post(
                path, headers=headers, json={"approve": True, "comment": "Verified with dispatcher"}
            ).status_code
            == 200
        )
        export = client.get(f"/api/requests/{run['id']}/export", headers=headers)
        assert export.status_code == 200
        assert export.json()["sources"] == ["delay.md"]
        assert client.get("/api/requests/absent", headers=headers).status_code == 404


def test_token_required(tmp_path):
    with pytest.raises(RuntimeError):
        create_app(tmp_path, token="short")


def test_provider_failure_can_be_retried(tmp_path):
    from langchain_core.runnables import RunnableLambda

    calls = []

    def model(_):
        calls.append(1)
        if len(calls) == 1:
            raise RuntimeError("provider timeout")
        return "Ask the carrier for a verified ETA."

    desk = Desk(tmp_path, POLICIES, RunnableLambda(model))
    with pytest.raises(RuntimeError):
        desk.create(REQUEST)
    run = desk.create(REQUEST)
    assert run["status"] == "awaiting_review"
    assert len(desk.list()) == 1
    desk.close()


def test_backup_uses_sqlite_snapshots_and_private_encryption(tmp_path, monkeypatch):
    import sqlite3
    import sys

    from freightdesk import backup

    desk = Desk(tmp_path, POLICIES)
    run = desk.create(REQUEST)
    desk.close()
    copies = {}

    class S3:
        def upload_file(self, path, bucket, key, ExtraArgs):
            assert bucket == "owned-backup-bucket"
            assert ExtraArgs == {"ServerSideEncryption": "AES256"}
            with sqlite3.connect(path) as db:
                assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
            copies[key] = Path(path).read_bytes()

    monkeypatch.setattr(backup.boto3, "client", lambda _: S3())
    monkeypatch.setattr(
        sys, "argv", ["backup", "--directory", str(tmp_path), "--bucket", "owned-backup-bucket"]
    )
    backup.main()
    restored = tmp_path / "restored"
    restored.mkdir()
    for key, content in copies.items():
        (restored / key.split("/")[-1]).write_bytes(content)
    recovered = Desk(restored, POLICIES)
    assert recovered.get(run["id"])["status"] == "awaiting_review"
    assert (
        recovered.review(run["id"], {"approve": True, "comment": "Recovery checked"})["status"]
        == "approved"
    )
    recovered.close()


def test_concurrent_reviews_cannot_overwrite_decision(tmp_path):
    from concurrent.futures import ThreadPoolExecutor

    desk = Desk(tmp_path, POLICIES)
    run = desk.create(REQUEST)

    def attempt(approve):
        try:
            return desk.review(run["id"], {"approve": approve, "comment": "Concurrent reviewer"})[
                "status"
            ]
        except ValueError:
            return "conflict"

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(attempt, [True, False]))
    assert results.count("conflict") == 1
    assert desk.get(run["id"])["status"] in ("approved", "rejected")
    desk.close()
