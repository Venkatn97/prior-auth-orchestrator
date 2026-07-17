cat > README.md << 'EOF'
# Prior Authorization Orchestrator

A production-shaped, multi-agent AI system that automates healthcare prior authorization decisions, from raw request intake through policy research, compliance checking, and human-in-the-loop approval.

## What it does

Given a raw prior authorization request (patient, procedure, diagnosis), the system:
1. Extracts structured data and checks insurance eligibility
2. Classifies urgency (routine vs. urgent)
3. Searches real payer policy documents via semantic RAG to determine if prior auth is required
4. Builds a documentation checklist and validates diagnosis coding
5. Drafts a human-readable summary and checks compliance
6. Auto-approves low-risk, compliant cases, or pauses for real human review on anything else
7. Resumes and finalizes once a human approves or rejects

## Architecture

10 agents across 3 clusters, orchestrated with LangGraph:

**Cluster A — Intake**
- Intake Parser: extracts patient/procedure/diagnosis from raw text (Claude via Bedrock)
- Eligibility Checker: calls an MCP tool for insurance eligibility lookup
- Urgency Classifier: routine vs. urgent (Claude via Bedrock)

**Cluster B — Clinical Review**
- Clinical Criteria Matcher: semantic RAG search over payer policies (custom chunking + HyPE), grounded Claude reasoning
- Documentation Gatherer: builds a required-documentation checklist from policy criteria
- Coding Validator: regex-based ICD-10 format check, then Claude-based clinical consistency check

**Cluster C — Decision**
- Auth Request Drafter: human-readable case summary
- Compliance Checker: deterministic rule-based gate (no LLM)
- Human Approver Gatekeeper: auto-approves clean routine cases; otherwise pauses execution via a real LangGraph `interrupt()` and waits for a human decision
- Submission/Closer: finalizes status and updates the audit trail

## Key technical pieces

- **MCP server** exposing eligibility lookup and policy search as standardized tools
- **RAG pipeline**: documents are split with *semantic chunking* (embedding-similarity-based boundaries, not fixed size), then each chunk gets *HyPE* (Hypothetical Prompt Embeddings) — Claude generates several questions each chunk would answer, and those questions (not the raw text) are embedded and indexed in Pinecone. Search matches question-to-question, then returns the original policy text.
- **Human-in-the-loop**: real pause/resume via LangGraph's `interrupt()` and a checkpointer — execution genuinely freezes and can be resumed later from a separate HTTP call, not a simulated status flag.
- **Guardrails**: every Claude call routes through a centralized client wired to an AWS Bedrock Guardrail that masks PII (names, SSNs, phone numbers) in both prompts and outputs.
- **Caching**: Redis cache-aside layer with TTL and stampede protection (single-flight locking) in front of the policy search — measured ~500x speedup on cache hits (560ms → <1ms).
- **Persistence**: full audit trail (every agent decision, every request's lifecycle status) written to Postgres on AWS RDS via SQLAlchemy + Alembic migrations.
- **Eval suite**: 15 automated pytest tests covering both clusters' happy paths, edge cases (invalid ICD-10 codes), and both branches of the human decision (approve/reject).

## Tech stack

LangGraph · FastAPI · AWS Bedrock (Claude) · AWS Bedrock Guardrails · Pinecone · Redis · PostgreSQL (AWS RDS) · SQLAlchemy · Alembic · Docker · AWS ECS Fargate · AWS ALB · AWS ACM · AWS ECR

## Deployment

Containerized with Docker and deployed on AWS ECS Fargate, fronted by an Application Load Balancer with a wildcard ACM certificate, served over HTTPS on a custom domain. IAM task roles (not static credentials) authorize the container's AWS access at runtime.

## Running locally

```bash
# infra
docker compose up -d          # Postgres + Redis

# env
cp .env.example .env          # fill in real values

# migrate
alembic upgrade head

# run
PYTHONPATH=. uvicorn api.main:app --reload --port 8000
```

## API
