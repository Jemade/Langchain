# FreightDesk

A dispatcher review workspace built with Python, LangChain, LangGraph and TypeScript.

Freight teams need to resolve delivery delays, damaged cargo and missing documents without promising an unverified ETA or an unauthorized refund. FreightDesk retrieves the applicable operating policy, prepares a draft and pauses for a dispatcher to inspect the evidence. Approval permits a JSON export. It does not send messages, release shipments or execute payments.

**Status:** runnable learning MVP. Policies, shipment examples and evaluation cases are fictional. The problem hypothesis needs validation with actual dispatchers. This repository has no customer adoption or production-readiness claim.

[Architecture](docs/ARCHITECTURE.md) · [AWS lab deployment](docs/AWS_DEPLOYMENT.md) · [Product validation](docs/VALIDATION.md)

## What works

- Three exception categories, authenticated API and a clean TypeScript review interface.
- LangChain `Document` records, BM25-scored policy retrieval and a prompt/model/parser pipeline for optional Amazon Bedrock drafts.
- LangGraph retrieve → draft → human review workflow, with durable SQLite checkpoints.
- Restart-safe pending reviews, reference deduplication and conflicting-reference rejection.
- Policy sources, retrieval scores, draft mode and workflow trace visible to reviewers.
- Approval-gated export; duplicate reviews fail rather than overwrite a decision.
- Offline deterministic demo, synthetic evaluation harness, Python/API tests and browser workflow test.
- Non-root Docker image, private S3 backup adapter and CloudFormation learning stack.

BM25 scores are ranking signals, not confidence probabilities. The supplied corpus has one policy per category; category filtering selects the applicable policy and BM25 ranks matches within that category. This is not a semantic vector search benchmark.

## Run locally

Python 3.11+ and Node.js 22+ are required. From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
export FREIGHTDESK_TOKEN="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
printf '%s\n' "$FREIGHTDESK_TOKEN"
uvicorn freightdesk.api:create_app --factory --host 127.0.0.1 --port 8000
```

Keep that terminal open. In a second terminal:

```bash
cd frontend
npm ci
npm run dev
```

Open http://127.0.0.1:5173, paste the token and select **Open workspace**. The token stays in browser memory. Use request `EXC-001`, shipment `HRE-1042`, category **Delivery delay** and report `The carrier reports a delay. No revised delivery time has been confirmed.` Inspect the draft and source, enter a review comment, approve or reject, then download an approved draft.

For Windows, activate with `.venv\Scripts\Activate.ps1` and set `$env:FREIGHTDESK_TOKEN` instead of using `export`. Generate the value with `python -c "import secrets; print(secrets.token_urlsafe(32))"`.

## Docker

After exporting `FREIGHTDESK_TOKEN`:

```bash
docker compose up --build
```

Open http://127.0.0.1:8000. A named volume preserves the databases across container restarts. Run one worker and one replica. `docker compose down` preserves the volume; `down -v` deletes it.

## Optional Bedrock mode

```bash
pip install -e '.[bedrock]'
export FREIGHTDESK_MODE=bedrock
export AWS_REGION=your-region
export BEDROCK_MODEL_ID=your-enabled-model-or-inference-profile
```

Authenticate with AWS SSO or an instance role before starting the API. Your account needs access to the chosen model and the relevant Bedrock invocation permissions. Bedrock may incur charges. No live Bedrock invocation is covered by the offline tests; model output can still hallucinate and needs review.

## Check the implementation

```bash
ruff check .
ruff format --check src tests scripts
pytest -q
python scripts/evaluate.py
cfn-lint infra/learning-stack.yaml
cd frontend
npm run build
npx playwright install chromium
npx playwright test
```

For the browser test, activate the Python virtual environment first and stop other servers on ports 8000 and 5173. The evaluation suite contains 60 synthetic demo-mode cases, not 60 independent real-world customer cases or an LLM quality score.

## Boundaries

Single operator, shared bearer token, local disk and serialized execution. No tenant isolation, per-user audit identity, external carrier integration, OCR or live tracking. Backups need a coordinated maintenance window to keep both databases aligned. Before public deployment, add user identity, authorization, TLS, rate controls, privacy review, workload testing and production database/checkpointer design.

See [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md). Credentials and runtime data must never be committed.
