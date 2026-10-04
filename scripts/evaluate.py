"""Offline, synthetic workflow checks; not a measurement of live LLM answer quality."""

import json
import tempfile
from pathlib import Path

from freightdesk.service import Desk


def main():
    cases = json.loads(Path("data/eval_cases.json").read_text())
    outcomes = []
    with tempfile.TemporaryDirectory() as directory:
        desk = Desk(Path(directory), Path("data/policies"))
        for case in cases:
            result = desk.create(case["request"])
            passed = (
                result["status"] == "awaiting_review"
                and result["evidence"][0]["source"] == case["source"]
                and case["required_phrase"] in result["draft"]
            )
            outcomes.append(
                {
                    "reference": case["request"]["reference"],
                    "passed": passed,
                    "sources": [e["source"] for e in result["evidence"]],
                }
            )
        desk.close()
    print(
        json.dumps(
            {
                "mode": "demo",
                "synthetic_cases": len(cases),
                "passed": sum(x["passed"] for x in outcomes),
                "results": outcomes,
            },
            indent=2,
        )
    )
    if not all(x["passed"] for x in outcomes):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
