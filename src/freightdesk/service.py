import json
import sqlite3
import threading
import uuid
from pathlib import Path

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command

from .evidence import PolicySearch
from .workflow import build_graph


class Desk:
    """Single-process workspace; lock serializes checkpoint writes and review decisions."""

    def __init__(self, directory: Path, policies: Path, model=None):
        directory.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        self.db = sqlite3.connect(directory / "requests.sqlite", check_same_thread=False)
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS requests (id TEXT PRIMARY KEY, "
            "reference TEXT UNIQUE NOT NULL, payload TEXT NOT NULL)"
        )
        self.db.commit()
        self.checkpoints = sqlite3.connect(
            directory / "checkpoints.sqlite", check_same_thread=False
        )
        self.graph = build_graph(PolicySearch(policies), SqliteSaver(self.checkpoints), model)

    def config(self, run_id):
        return {"configurable": {"thread_id": run_id}}

    def get(self, run_id):
        with self.lock:
            row = self.db.execute("SELECT payload FROM requests WHERE id = ?", (run_id,)).fetchone()
            if not row:
                raise KeyError(run_id)
            state = self.graph.get_state(self.config(run_id))
            return {"id": run_id, **state.values, "status": state.values.get("status", "pending")}

    def create(self, request):
        encoded = json.dumps(request, sort_keys=True)
        with self.lock:
            row = self.db.execute(
                "SELECT id,payload FROM requests WHERE reference = ?", (request["reference"],)
            ).fetchone()
            if row:
                if row[1] != encoded:
                    raise ValueError("reference already used for a different request")
                run_id = row[0]
            else:
                run_id = str(uuid.uuid4())
                self.db.execute(
                    "INSERT INTO requests VALUES (?, ?, ?)", (run_id, request["reference"], encoded)
                )
                self.db.commit()
            state = self.graph.get_state(self.config(run_id))
            if not state.values:
                self.graph.invoke({"request": request}, self.config(run_id))
            elif state.next and state.values.get("status") != "awaiting_review":
                # Resume a failed node after a provider error, preserving checkpoints.
                self.graph.invoke(None, self.config(run_id))
            return self.get(run_id)

    def list(self):
        with self.lock:
            ids = self.db.execute(
                "SELECT id FROM requests ORDER BY rowid DESC LIMIT 100"
            ).fetchall()
            return [self.get(row[0]) for row in ids]

    def review(self, run_id, decision):
        with self.lock:
            current = self.get(run_id)
            if current["status"] != "awaiting_review":
                raise ValueError("request is not awaiting review")
            self.graph.invoke(Command(resume=decision), self.config(run_id))
            return self.get(run_id)

    def close(self):
        self.db.close()
        self.checkpoints.close()
