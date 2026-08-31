# Asgard — Local-first AI Operations Platform

Asgard is a bounded software Proof for operating asynchronous AI analysis jobs through a Java/Python event-driven stack.

The accepted v1.0 implementation evidence focuses on an **operable AI Job lifecycle**, not on the number of AI providers or on production-readiness claims.

```text
Input / Log
  → Heimdall
  → Persistent Analysis Job
  → Kafka
  → Bifrost
  → Local AI (Ollama)
  → Result Event
  → Persistence
  → Operator / Metrics

Failure
  → FAILED / DLQ
  → Controlled Redrive
  → Audit
  → Retry
  → SUCCEEDED
```

> Current authoritative project state and accepted evidence are defined in [`ASGARD_MASTER.md`](ASGARD_MASTER.md). Historical roadmap or implementation documents are context only when they conflict with that Master.

## Proof status

**Implementation / Proof Candidate Ready — Human Review Required**

Accepted v1.0 use cases:

| Use case | Result | Accepted boundary |
| --- | --- | --- |
| UC-01 Startup | PASS | required core services healthy through PR-visible execution |
| UC-02 Local AI Analysis | PASS | persistent Job → Kafka → real Ollama → result persistence → `SUCCEEDED` |
| UC-03 Local-first Policy | PASS | default/sensitive/cloud-disabled paths remain local with no external provider invocation |
| UC-04 Recovery | PASS | `FAILED` / DLQ → authorized redrive → audit → retry → `SUCCEEDED`, with duplicate-redrive visibility |
| UC-05 Observability | PASS | bounded lifecycle counters observed through Prometheus and existing Grafana path rendered |

The current repository does **not** claim production readiness from these bounded proof runs. Final external-presentation acceptance is controlled by the Human Review gate in `ASGARD_MASTER.md`.

## Verified capability boundary

The accepted repository evidence supports these claims:

- event-driven Java/Python AI operations architecture;
- persistent asynchronous Analysis Job lifecycle;
- Kafka request/result handoff;
- real local Ollama inference in the accepted local AI path;
- result persistence and final Job state;
- fail-closed Local-first routing under the accepted configuration;
- bounded `FAILED` / DLQ → Redrive → Audit → Retry → `SUCCEEDED` recovery;
- duplicate redrive visibility through `SKIPPED` audit behavior;
- bounded live lifecycle metrics through Prometheus;
- existing Grafana datasource/dashboard path with visible lifecycle panels;
- authentication/rate-limit boundaries where exercised by the accepted workflow;
- a minimal executable frontend boot shell as part of the verified stack boundary.

## Accepted evidence

### UC-02 — Real local AI golden path

- Issue #13 — CLOSED / COMPLETED
- PR #14 — MERGED
- dedicated proof run `32323663891` — SUCCESS
- primary CI `32323664031` — SUCCESS
- artifact `9390712782`
- digest `sha256:66840ffe978f0a6d011b1440e7960962da530f352cc68da8e23744bf50d212da`

Executed path:

`Analysis Job → Kafka → Bifrost → real Ollama smollm:135m → result event → persistence → SUCCEEDED`

Fallback-only output was not accepted as the UC-02 success condition.

### UC-03 — Local-first policy boundary

- Issue #17 — CLOSED / COMPLETED
- PR #18 — MERGED
- dedicated proof run `32945550180` — SUCCESS
- primary CI `32945550197` — SUCCESS
- artifact `9598234317`
- digest `sha256:94ce477579261ee28cd9bec30e17d2397628158b5ba85e3a8fa168cd44b32c01`

Accepted execution showed default, sensitive, and cloud-hint-disabled requests use the local `on_device_rag / ollama` path through production dispatch with non-empty real results. `ENABLE_CLOUD_LANE=false`; the cloud answerer was not initialized and no external provider was invoked.

### UC-04 — Recovery golden path

- Issue #19 — CLOSED / COMPLETED
- PR #20 — MERGED
- dedicated recovery proof `32967543925` — SUCCESS
- primary CI `32967543793` — SUCCESS
- artifact `9606403831`
- digest `sha256:a641015cdb0fa2cabebc49e27da456e93c4ecce5d4b7dff1ccb976604f00e2ec`

Executed path:

`Analysis Job → deterministic failure → persisted FAILED → authorized redrive → attempt 0 → 1 → Kafka retry → Bifrost → real Ollama → persisted SUCCEEDED → SUCCESS audit`

A duplicate redrive produced a `SKIPPED` audit result without incrementing the attempt. The proof also exposed and corrected an audit pre-state snapshot bug.

### UC-05 — Prometheus / Grafana observability

- Issue #21 — CLOSED / COMPLETED
- PR #22 — MERGED
- dedicated proof run `33009550844` — SUCCESS
- primary CI `33009550928` — SUCCESS
- evidence artifact `9622043567`
- digest `sha256:783c37b1bd7079edce01caa61e5ab767826d195cb4a3b800e87ee0cb0c1262a8`

Observed live through Prometheus in the accepted proof:

```text
ai_job_requested_total = 1
ai_job_success_total = 1
ai_job_failed_total = 1
ai_job_redriven_total = 1
up{job="heimdall"} = 1
```

The existing Grafana datasource/dashboard path rendered the Jobs Requested / Succeeded / Failed / Redriven panels. The durable evidence artifact was inspected as synthetic-safe and without visible PII or secrets.

Short-window Grafana `increase(...)` / rate-style panels may display `0` for this single-event proof window even when the current Prometheus counter is `1`. This evidence proves the bounded metrics/dashboard path, not production dashboard calibration or SLO maturity.

## Architecture boundary

Core v1.0 proof components include:

- **Heimdall** — Java / Spring Boot gateway and AI Job lifecycle boundary;
- **Bifrost** — Python AI execution service;
- **Kafka** — asynchronous request/result handoff;
- **PostgreSQL** — persistent Job/result state;
- **Ollama** — accepted local inference provider;
- **Prometheus / Grafana** — bounded operating visibility;
- supporting infrastructure used by the accepted startup path, including Redis and Elasticsearch.

The repository may contain historical or experimental modules beyond this boundary. Their existence does not make them accepted v1.0 Proof claims.

## Historical cloud experiment

AWS/Bedrock work is **deferred and not required for Asgard v1.0 acceptance**.

- historical Issue #15 — CLOSED / NOT PLANNED;
- historical PR #16 — CLOSED / NOT MERGED;
- AWS `AssumeRoleWithWebIdentity` — NOT VERIFIED;
- STS caller identity — NOT VERIFIED;
- real Bedrock invocation/result — NOT VERIFIED;
- OpenAI/Gemini or other cloud-provider execution — NOT VERIFIED as part of accepted v1.0 Proof.

No static cloud credential or replacement cloud provider is required to complete the current Local-first v1.0 scope.

## Explicit non-claims / limitations

The current Proof does **not** establish:

- production readiness;
- enterprise operational readiness;
- legal GDPR or security compliance certification;
- production SLA/SLO;
- stable latency, throughput, or cost-saving percentages;
- production Kubernetes, HA, autoscaling, or multi-region readiness;
- accepted cloud-provider execution;
- a full operational/admin dashboard product;
- unattended autonomous operations;
- production observability calibration from the short synthetic UC-05 window.

Additional known boundaries:

- hosted CPU Ollama latency varies; no stable performance claim is made;
- broad pre-existing Heimdall Checkstyle debt remains outside the bounded v1.0 Proof unless a future required gate depends on it;
- legacy AWS/cloud code may remain in the repository without being part of accepted execution evidence;
- `ai_job_duplicate_result_total` was not observed live in UC-05 and is not claimed as such.

## Reproduction and repository guidance

This repository contains historical scripts and documentation from earlier development phases. Before using an old quick-start or roadmap statement as an acceptance claim, compare it with [`ASGARD_MASTER.md`](ASGARD_MASTER.md).

For the current v1.0 Proof, the evidence hierarchy is:

1. current repository and executable evidence;
2. `ASGARD_MASTER.md`;
3. accepted Issue / PR / workflow evidence;
4. this README;
5. historical roadmap, completion, or implementation documents.

## License

See [`LICENSE`](LICENSE).
