# Asgard Single-node Delivery Handoff

> Bounded post-v1.0 operator handoff for the accepted Local-first path. This document does not broaden the frozen v1.0 claim boundary.

## Supported boundary

This handoff covers one technical operator on one Linux host using the repository's accepted local proof path. It covers PostgreSQL/Kafka/Redis/Elasticsearch dependencies, Heimdall, Bifrost, and real local Ollama inference. It does **not** claim AWS/Bedrock/OIDC/cloud execution, Kubernetes/HA/multi-node recovery, autonomous operations, production SLA/SLO, or legal/security certification.

## Prerequisites

The executable source of truth is `scripts/local-proof.sh`. Its preflight currently requires:

- Linux shell with Bash;
- Docker daemon and Docker Compose plugin;
- Java 21;
- Python 3.8+ with `venv` support;
- `curl`;
- free local ports `5432`, `6379`, `8080`, `8000`, `9091`, and `9200`.

The proof runner builds Heimdall, creates an isolated Python environment for Bifrost, starts the required Compose infrastructure, and uses real Ollama inference. The accepted CI wrapper is `.github/workflows/v11-m1-local-proof.yml`.

## Configuration ownership

- Repository defaults/examples define the bounded proof configuration; do not infer production secret-management guarantees from them.
- `ASGARD_PROOF_MODEL` selects the local Ollama model; accepted proof evidence used `smollm:135m`.
- `ASGARD_PROOF_OUTPUT` selects the synthetic-safe summary path.
- `ASGARD_PROOF_EVIDENCE_DIR` selects failure-evidence output.
- `ASGARD_PROOF_WORK_DIR` may point at a caller-owned **empty** directory. The runner refuses non-empty caller-owned content.
- `ASGARD_PROOF_KEEP=1` preserves the proof environment/work directory for inspection. Default cleanup removes proof-owned processes, containers/volumes, and temporary work.

## Start and execute one real Local AI Job

From the repository root:

```bash
bash -n scripts/local-proof.sh
bash scripts/local-proof.sh
```

A successful run must end with the script's PASS summary and a real Local-first Job path through Heimdall → Kafka → Bifrost → Ollama → persisted final Job state. Code existence or an agent report is not a substitute for the executable result.

For retained inspection during a handoff session:

```bash
ASGARD_PROOF_KEEP=1 \
ASGARD_PROOF_OUTPUT="$PWD/local-proof-summary.json" \
ASGARD_PROOF_EVIDENCE_DIR="$PWD/local-proof-evidence" \
bash scripts/local-proof.sh
```

Use `ASGARD_PROOF_KEEP=1` deliberately: retained processes/containers require operator cleanup after inspection.

## Inspect result and health

The proof runner performs its own readiness and final persisted Job checks. Treat its generated summary as the bounded handoff result. For failure diagnosis, inspect the configured evidence directory; on failure the runner preserves `failure-context.json` plus available Heimdall/Bifrost/Ollama/final-Job diagnostics.

Do not convert one proof run into stable latency, throughput, cost, availability, or SLO claims.

## Supported restart semantics

M4 accepted one bounded single-node case: Bifrost was killed after it entered processing, confirmed down, then restarted with the same Kafka consumer-group semantics; the persisted target Job subsequently reached `SUCCEEDED` with a result reference. The executable reference is `.github/workflows/v11-m4-bifrost-restart.yml`.

This proves **that bounded replay case only**. It does not prove Kafka outage recovery, multi-node failover, HA, recovery-time objectives, or unattended autonomous retry.

For a delivery review, use the M4 workflow as the executable restart reference rather than inventing a second process-management/deployment path.

## Persistence and cleanup

- Job/result state is persisted through the accepted Heimdall/PostgreSQL path.
- Kafka participates in request/result handoff; M4 validates one replay-after-Bifrost-kill case.
- The default local proof cleanup uses `docker compose ... down -v`, so proof-owned Compose volumes are intentionally removed after the run.
- `ASGARD_PROOF_KEEP=1` retains the environment for bounded inspection; the operator then owns cleanup.
- **Backup/restore: NOT VERIFIED.** Do not represent proof-volume persistence or retained inspection state as a tested backup/restore procedure.

## Troubleshooting

| Symptom | Bounded action |
|---|---|
| `missing required command` | Install the named prerequisite and rerun preflight. |
| `Docker daemon is not available` | Start/fix the local Docker daemon; do not bypass the check. |
| `Docker Compose plugin is required` | Install/enable Compose v2 and rerun. |
| `Java 21 required` | Select a Java 21 runtime before rerunning. |
| `required port already in use` | Stop the conflicting local process or use a clean host/session; the accepted proof expects those ports. |
| caller-owned work directory rejected | Supply an empty directory or omit `ASGARD_PROOF_WORK_DIR`. |
| infrastructure/readiness failure | Inspect `local-proof-evidence/` (or configured evidence path) before changing runtime code. |
| Ollama/model failure | Check retained Ollama/pull diagnostics; do not substitute a cloud provider and call the Local-first gate PASS. |
| Bifrost interruption/restart question | Use the accepted M4 workflow semantics; do not generalize beyond the proven single-node case. |
| broad Heimdall Checkstyle RED | Known pre-existing debt unless a selected milestone makes that gate material; do not mass-fix as handoff work. |

## Exact references

- Local proof runner: `scripts/local-proof.sh`
- M1 CI wrapper: `.github/workflows/v11-m1-local-proof.yml`
- M4 restart proof: `.github/workflows/v11-m4-bifrost-restart.yml`
- Authoritative progression/claim contract: `ASGARD_MASTER.md`

## Explicitly not verified by this handoff

Production readiness; production SLA/SLO; stable performance/cost; backup/restore; Kubernetes/HA/multi-node recovery; cloud-provider execution; enterprise identity/RBAC; legal/security certification; unattended autonomous operations.
