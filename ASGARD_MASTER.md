# ASGARD MASTER

> **Authoritative execution and progression contract**
>
> Single source of truth for the frozen Asgard v1.0 Proof baseline and bounded post-v1.0 progression. Current repository / Issue / PR / executable evidence overrides README claims, historical roadmap text, old portfolio positioning, Scheduled Task prompt text, and agent self-report.

## 0. Control

- **Frozen Baseline**: Asgard v1.0 — Wishket / Freelance Proof
- **Frozen Baseline Level**: READY TO SHOW bounded software Proof
- **Frozen v1.0 Product Direction**: **Local-first AI Operations Platform**
- **Post-v1.0 Product Destination**: **bounded single-node Local AI Operations Tool for a technical operator**
- **Current Phase**: **DESTINATION REACHED — BOUNDED SINGLE-NODE TOOL**
- **Current Batch**: none — D1 accepted / D2 progression review pending
- **Current Status**: **v1.0 FROZEN / M1–M12 FROZEN — DESTINATION REACHED — BOUNDED SINGLE-NODE TOOL**
- **Repo**: `joeylife94/asgard`
- **Branch**: `main`
- **Accepted implementation main SHA**: `cc5cd10722a4c629da75e90ca0fa4daa05b75a01`
- **Accepted buyer-facing proof/docs main SHA**: `359b26e573e5da04b2d0ec406a56be7ecb508dbd`
- **Accepted M1 exact PR head**: `0db87a1a1feb54bf677533d88516d72f3bda73ec`
- **Accepted M1 merge main SHA**: `3e90bbd7eedca5f71c341ea91691b0cf2bc121ab`
- **Accepted M2 exact PR head**: `224e53814bc33e565189acd0b2c45866be32f2a0`
- **Accepted M2 merge main SHA**: `07875ef2c9f6784d54c23c2bb19b326d2ff6ed86`
- **Accepted M3 exact PR head**: `b4e79a00dc3677746a244a08c6fd36dfccba620c`
- **Accepted M3 merge main SHA**: `c97dfa2d79f81b7b0172833769a71164934a103e`
- **Accepted M4 exact PR head**: `e46f11cc9cccd7763cc8d6e7b3dbcd8907af934b`
- **Accepted M4 merge main SHA**: `d853f8b5fe248ee2e0fd0032f6e0ffccadc5f578`
- **Accepted M5 exact PR head**: `b13438d91ca13ac9a889bad4f31a2b33550533e9`
- **Accepted M5 merge main SHA**: `3f6eb40793991adba82c7d5b60920a5f60c80a04`
- **Accepted M6 exact PR head**: `08c047b35c55b693615d3bdf055a0250d838817a`
- **Accepted M6 merge main SHA**: `cbd8a1ef74ae55b5636b81ecbf757e50adb268da`
- **Accepted M7 exact PR head**: `c4de490bab6d1f3709cf7ce32c4d7b2212131fce`
- **Accepted M7 merge main SHA**: `5ec343a52d58e61b4c2354f7b05a9cf581c4c0d7`
- **Accepted M8 exact PR head**: `5fb86a99a2e98f237c0d516391128ef9a86bd500`
- **Accepted M8 merge main SHA**: `5748d33953c7b46abd945d682618a409c7b9125b`
- **Accepted M9 exact PR head**: `c68c246c2d86672451425b5bb459234cb263794d`
- **Accepted M9 merge main SHA**: `05ed2bea167153c30a403a18a55f742149ebec7f`
- **Accepted M10 exact PR head**: `bc06a16145897884c3c0be2bf78ee214477bc89a`
- **Accepted M10 merge main SHA**: `8abd9b6cf4ee23a80c86a28a305c2c873c8de025`
- **Accepted M11 exact PR head**: `a6d62af5071010ebcb6ec7f7848be869a08843b9`
- **Accepted M11 merge main SHA**: `96b27d105dc0453b33a00f8d7259b789b836b29b`
- **Accepted M12 exact PR head**: `58c57c96c9c32049e6cf4df4d2149dafbc20e96f`
- **Accepted M12 merge main SHA**: `649207c81f1fecbfd251ba59ab55826117b722ff`
- **Active Implementation Issue**: none
- **Active Implementation PR**: none
- **Selected Next Milestone**: none — D1 destination reached; perform D2 destination review before opening work
- **Human Review truthfulness item**: Issue #23 CLOSED / COMPLETED; PR #24 MERGED
- **Historical AWS work item**: Issue #15 CLOSED / NOT PLANNED; PR #16 CLOSED / NOT MERGED
- **Updated**: 2026-09-03
- **Final v1.0 Gate**: **PASS — FREEZE APPROVED**
- **Post-v1.0 Gate**: **M1–M12 PASS / ACCEPTED / FROZEN — DESTINATION REACHED — BOUNDED SINGLE-NODE TOOL**

---

# 1. Product Definition

**Asgard는 운영 로그와 이벤트를 영속적인 비동기 Job으로 처리하고, Kafka 기반 실행 흐름과 Local LLM 분석, 결과 저장, 실패 복구, 감사 및 관측 기능을 제공하는 Local-first AI Operations Platform이다.**

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

Asgard v1.0의 중심 Proof는 **AI provider 수가 아니라 운영 가능한 AI Job lifecycle**이다. Post-v1.0 progression은 이 baseline을 무한 확장하지 않고, 기술 운영자가 단일 로컬/서버 환경에서 재현 가능하게 설치·실행·조회·복구·감사·진단할 수 있는 bounded operational tool로 발전시키는 데 한정한다.

---

# 2. Frozen v1.0 Boundary

## Core Must Pass — COMPLETE
- Heimdall / Bifrost
- PostgreSQL / Kafka
- Local Ollama provider
- persistent Analysis Job lifecycle
- result persistence / idempotency boundary
- fail-closed local-first routing boundary
- DLQ / Redrive / Audit
- Auth / Rate Limit where used by the bounded workflow
- Prometheus / Grafana operating visibility
- minimal executable frontend boot shell only
- CI / E2E evidence
- buyer-facing truthfulness review at the final Human Review gate

## Explicitly Deferred / Not Required for v1.0
- AWS Bedrock / AWS OIDC / IAM role setup / real cloud-provider execution
- replacing AWS with OpenAI / Gemini / another cloud provider
- multi-provider routing expansion
- RAG as the primary Asgard Proof
- advanced React admin dashboard
- HP AI Server reference deployment
- Kubernetes production / HA / autoscaling / multi-region
- Keycloak / Vault / enterprise secret-manager work
- full RBAC / multi-tenancy
- production SLA/SLO
- legal GDPR or security certification

Historical cloud code may remain in the repository. **Its existence does not make cloud execution a v1.0 requirement or accepted claim.** The v1.0 boundary is permanently preserved as a frozen verified baseline. Post-v1.0 work must not rewrite historical v1.0 PASS claims, accepted evidence, or non-claims.

---

# 3. Frozen v1.0 Accepted Evidence

| Use case | Accepted evidence | Current |
|---|---|---|
| UC-01 Startup | PR #12; PostgreSQL/Kafka/Redis/Elasticsearch/Prometheus/Grafana/Heimdall/Bifrost/frontend reachability | **PASS** |
| UC-02 Real Local AI | PR #14 merge `ee24e6990d19c0be618baf1698bff275a8b27134`; run `32323663891`; artifact `9390712782` / `sha256:66840ffe978f0a6d011b1440e7960962da530f352cc68da8e23744bf50d212da` | **PASS** |
| UC-03 Local-first Policy | PR #18 merge `a7e079872004c6dcf73cdf36d105aabde37fbb8d`; accepted head `b6fc2c2f15f0d65ba6f314525740a63cc42c24ce`; run `32945550180`; artifact `9598234317` / `sha256:94ce477579261ee28cd9bec30e17d2397628158b5ba85e3a8fa168cd44b32c01` | **PASS** |
| UC-04 Recovery | PR #20 merge `37c29223044100c216372d27169eba0c3c0a0dc0`; accepted head `4b3bf88b31ae7392004121817832b232f4cd8e21`; run `32967543925`; artifact `9606403831` / `sha256:a641015cdb0fa2cabebc49e27da456e93c4ecce5d4b7dff1ccb976604f00e2ec` | **PASS** |
| UC-05 Observability | PR #22 merge `cc5cd10722a4c629da75e90ca0fa4daa05b75a01`; accepted head `e1509b7cefdb47a057c25051c16409b030c11dee`; run `33009550844`; artifact `9622043567` / `sha256:783c37b1bd7079edce01caa61e5ab767826d195cb4a3b800e87ee0cb0c1262a8` | **PASS** |
| Human Review | Issue #23 CLOSED; PR #24 merge `359b26e573e5da04b2d0ec406a56be7ecb508dbd`; CI `33371042786`; CI/CD `33371042762` | **PASS — HUMAN REVIEW PASSED** |

**ASGARD PROOF v1.0 CLOSED / FREEZE — HUMAN REVIEW PASSED.**

Supported claims remain limited to the accepted Local-first asynchronous Job lifecycle, result persistence, fail-closed routing, bounded DLQ/redrive/audit recovery, and bounded observability. Not verified: production readiness, enterprise operational readiness, legal compliance certification, production SLA/SLO, stable latency/throughput/cost, Kubernetes/HA/multi-region, cloud-provider execution, full admin platform, or unattended autonomous operations.

---

# 4. Known Risks / Holds

| ID | Risk | Handling |
|---|---|---|
| R-001 | duplicate `idx_severity` schema index name | known non-fatal debt; touch only if a future accepted requirement fails on it |
| R-002 | broad Heimdall Checkstyle/build debt | pre-existing; no mass-fix without a required gate |
| R-003 | startup script / proven CI invocation drift | M1 closed the accepted bounded Linux path; broader convenience only when required |
| R-004 | README / historical docs may overclaim | README closed via Issue #23 / PR #24; historical docs non-authoritative |
| R-005 | hosted CPU Ollama latency variability | bounded generation only; no stable performance claims |
| R-006 | ingestion auto-analysis may create extra job | proof paths isolate target Job where required |
| R-007 | legacy AWS/Bedrock code remains | DEFER; not an automatic progression target |
| R-008 | duplicate routing generations | no refactor without a milestone requirement |
| R-009 | agent self-report | never substitute for executed evidence |
| R-010 | redrive audit pre-state correctness | CLOSED for accepted UC-04 (`FAILED / 0`) |
| R-011 | short-window Grafana delta/rate semantics | do not generalize into production observability claims |
| R-012 | M2 console bounded/read-only by default | recovery only under explicit M3 feature flag |
| R-013 | proof harness queue-order race | bounded harness isolation only; no autonomous-runtime guarantee |
| R-014 | M4 Bifrost restart proof is one bounded single-node replay case | no HA/Kafka-outage/recovery-time generalization |
| R-015 | backup/restore gap after M5 | CLOSED for one bounded M6 PostgreSQL backup/restore case only; DR/PITR/RPO/RTO remain unverified |
| R-016 | M7 diagnostic snapshot proves one bounded read-only support bundle | no alerting, autonomous remediation, generic monitoring-platform, production monitoring/SLA/SLO claim |
| R-017 | M8 Kafka restart proof is one bounded persisted-request replay case | no multi-broker/HA/autonomous failover/recovery-time/production-durability generalization |
| R-018 | M9 PostgreSQL restart proof is one bounded same-volume recovery case | no replication/HA/PITR/DR/RPO-RTO/recovery-time/production-durability generalization |
| R-019 | stale single-node handoff truth after M6/M8/M9 | CLOSED by accepted M10 handoff truth reconciliation; no claim expansion |
| R-020 | broad `infrastructure` CI/CD filter caused unrelated workflow/script changes to execute Heimdall/Bifrost application builds | CLOSED by accepted M11 change-scoped signal isolation; R-002 remains visible when Heimdall/shared Gradle inputs actually change |
| R-021 | retained proof cleanup logic is duplicated in handoff/workflow snippets and requires manual session metadata handling | CLOSED by accepted M12 repository-owned retained cleanup command; executable evidence is bounded to proof-owned retained sessions and does not establish generic host/process-management safety |

---

# 5. Work Item / PR Lifecycle

1. MASTER first.
2. Current repository / Issue / PR / executed evidence overrides stale checkpoint text and Scheduled Task self-report.
3. One bounded implementation/proof Issue at a time.
4. Active relevant PR before new work.
5. Define executable Acceptance Criteria before implementation.
6. RED → first concrete failure → smallest in-scope correction.
7. Exact-head GREEN + bounded diff + clean review/security → merge with expected-head guard.
8. Close Issue only after accepted evidence exists.
9. Reconcile MASTER on `main` after merge.
10. Evaluate Milestone Acceptance before selecting another Issue.
11. Frozen accepted milestone becomes a preserved baseline slice; **FREEZE does not mean project development ends**.
12. After acceptance, return to Destination/Progression Review and select another bounded milestone only when it materially advances the current product-level destination.
13. Do not manufacture work for activity or accumulate test-only variants after a destination is already supported.

---

# 6. Post-v1.0 Progression Contract

## Product Destination D1 — ACCEPTED
> **A bounded, single-node Local AI Operations Tool that a technical operator can reproducibly run, use for real Local Ollama jobs, inspect job/result state, perform controlled recovery, audit/diagnose the system, preserve/restore bounded persistence, and cleanly hand off/tear down without requiring a cloud AI provider.**

**DESTINATION REACHED — BOUNDED SINGLE-NODE TOOL.**

Accepted evidence now spans reproducible Local-first execution and real Ollama work, bounded read-only inspection, controlled recovery/audit, Bifrost/Kafka/PostgreSQL restart cases, delivery handoff, one bounded PostgreSQL backup/restore case, diagnostic snapshot, truthful handoff reconciliation, change-scoped CI signal isolation, and repository-owned retained-proof cleanup.

## Farther Destination D2 — REVIEW PENDING
> **Versioned Single-node Delivery Candidate** — one bounded delivery package/acceptance path that a clean technical environment can use without private tribal knowledge to obtain the accepted single-node workflow: start/preflight → real Local AI job → inspect → controlled recovery/audit → diagnostics → bounded backup/restore where claimed → cleanup, with explicit version/provenance and limitations.

D2 must reuse existing accepted assets first. Do not add another isolated lifecycle/restart/cleanup variant unless it is a concrete blocker to this coherent delivery candidate. A versioned CI artifact/bundle and truthful handoff contract are acceptable; packaging alone does not create production/enterprise claims.

After D2, if meaningful progression requires multi-user identity/RBAC, public production deployment, cloud providers, HA/Kubernetes, SLA/SLO, or another major product-direction/security choice, stop at **HUMAN REVIEW — NEXT DESTINATION DECISION**.

Priority: coherent delivery/use evidence → only concrete blockers → no micro-loop accumulation.

Do not automatically select AWS/Bedrock/OIDC/IAM, OpenAI/Gemini cloud expansion, Kubernetes/HA/autoscaling/multi-region, multi-tenancy, full RBAC/SSO, billing, autonomous operations, broad RAG, generic refactors, broad Checkstyle cleanup, or full admin-platform competition.

---

# 7. Accepted Post-v1.0 Milestones

| Milestone | Issue / PR | Accepted exact head | Merge main SHA | Executed evidence | Boundary |
|---|---|---|---|---|---|
| M1 — Local Reproduction & First Job | #25 / #30 | `0db87a1a1feb54bf677533d88516d72f3bda73ec` | `3e90bbd7eedca5f71c341ea91691b0cf2bc121ab` | M1 `33399015962`; primary CI `33399015985`; artifact `9760584618` / `sha256:f8011b67f5c49a87ddef93356295d403d37d4dc731b82811bfe087c2399c361` | bounded GitHub-hosted Linux path only |
| M2 — Read-only Job Lifecycle Console | #31 / #32 | `224e53814bc33e565189acd0b2c45866be32f2a0` | `07875ef2c9f6784d54c23c2bb19b326d2ff6ed86` | M2 `33405406557`; artifact `9763096595` / `sha256:ff363841b4c4754870ab40a33f630284e39b3820123d503e847096ccc1e19b05` | bounded read-only console, not full admin |
| M3 — Controlled Recovery Workflow | #33 / #35 | `b4e79a00dc3677746a244a08c6fd36dfccba620c` | `c97dfa2d79f81b7b0172833769a71164934a103e` | M3 `33422708481`; artifact `9769683333` / `sha256:2c1bdfe47287dc3e88061259ee2d93f9b8025310721e3a2b66b7ae3fd05d6d78` | explicit operator redrive only; no autonomous retry claim |
| M4 — Bifrost Restart | #36 / #38 | `e46f11cc9cccd7763cc8d6e7b3dbcd8907af934b` | `d853f8b5fe248ee2e0fd0032f6e0ffccadc5f578` | M4 `33444318573`; artifact `9777540907` / `sha256:d1a078d52d9fb70a3c9931f6e5065e2fd4220f863fffbf5acc1e1ba07d020ea4` | one bounded Bifrost kill/restart replay case |
| M5 — Single-node Delivery Handoff | #39 / #40 | `b13438d91ca13ac9a889bad4f31a2b33550533e9` | `3f6eb40793991adba82c7d5b60920a5f60c80a04` | M5 `33652535194`; artifact `9855507091` / `sha256:f26aa953bcb5a855bc4f628ec1edd56f7e61a750a432ed0d2e4d12a7fbc09683` | repository-owned Linux handoff; later milestones add bounded evidence only |
| M6 — PostgreSQL Backup/Restore | #41 / #42 | `08c047b35c55b693615d3bdf055a0250d838817a` | `cbd8a1ef74ae55b5636b81ecbf757e50adb268da` | M6 `33664446061`; artifact `9860123355` / `sha256:d9e7bb833ed1eaa265baa19bead70b528762c0939160e17c30013385be7c668c` | one bounded backup/restore case; no DR/PITR/RPO-RTO |
| M7 — Operator Diagnostic Snapshot | #43 / #44 | `c4de490bab6d1f3709cf7ce32c4d7b2212131fce` | `5ec343a52d58e61b4c2354f7b05a9cf581c4c0d7` | M7 `33693038558`; artifact `9870849376` / `sha256:4961998526b32c5af5cf7b39f8df9159e2cb7c13bdb71743a5116e5bec5ec30b` | one bounded read-only support bundle |
| M8 — Kafka Restart Recovery | #45 / #46 | `5fb86a99a2e98f237c0d516391128ef9a86bd500` | `5748d33953c7b46abd945d682618a409c7b9125b` | M8 `33697888620`; artifact `9872527893` / `sha256:0b7827a743fc08e9e583c904c848ca622a02137d487bca4b63d1e6eaef3be486` | one single-broker persisted-request replay case; no HA/multi-broker claim |
| M9 — PostgreSQL Restart Recovery | #47 / #48 | `c68c246c2d86672451425b5bb459234cb263794d` | `05ed2bea167153c30a403a18a55f742149ebec7f` | M9 `33702303430` SUCCESS; artifact `9874023335` / `sha256:1ce95b2a206500ab8de72d9af54bb778b1b0128e3a2e7edd0edc3d2f9537151c`; Bifrost and relevant security/quality gates independently GREEN while broad Heimdall R-002 remained separately classified | one proof-owned same-volume PostgreSQL restart/recovery case; no replication/HA/PITR/DR/RPO-RTO/SLA-SLO/production durability/cloud claim |
| M10 — Single-node Handoff Truth Reconciliation | #49 / #50 | `bc06a16145897884c3c0be2bf78ee214477bc89a` | `8abd9b6cf4ee23a80c86a28a305c2c873c8de025` | M10 `33713410047` SUCCESS; M5 handoff regression `33713410083` SUCCESS; primary CI `33713410094` SUCCESS; Local AI golden path `33713409968` SUCCESS; broad CI/CD `33713410364` RED only at pre-existing Heimdall R-002 with Bifrost and dependency security GREEN | delivery-facing truth reconciliation only; no runtime capability or production/HA/DR/cloud claim expansion |
| M11 — Change-scoped CI/CD Signal Isolation | #51 / #52 | `a6d62af5071010ebcb6ec7f7848be869a08843b9` | `96b27d105dc0453b33a00f8d7259b789b836b29b` | CI/CD `33721456071` SUCCESS; primary CI `33721456054` SUCCESS | workflow-only changes no longer force unrelated application builds; direct service/shared-input gates and R-002 visibility remain bounded by actual changed inputs |
| M12 — Retained Proof Cleanup Command | #53 / #54 | `58c57c96c9c32049e6cf4df4d2149dafbc20e96f` | `649207c81f1fecbfd251ba59ab55826117b722ff` | M12 `33736638004` SUCCESS; artifact `9886113574` / `sha256:0313cef7765963493d890be046f23f3a7d1747af3037080a8f1e612c140b87b2`; M10 handoff truth `33736638010` SUCCESS; M5 delivery handoff `33736638012` SUCCESS; primary CI `33736638000` SUCCESS; Real Local AI Golden Path `33736638005` SUCCESS; CI/CD `33736637997` SUCCESS | proof-owned retained-session cleanup only; metadata parsed as data, PID ownership verified before signaling; no generic process manager, production operations, HA/DR/SLA-SLO/cloud claim |

**M1–M12 PASS / ACCEPTED / FROZEN.**

---

# 8. Destination D1 Acceptance — REACHED

## Destination
`A bounded, single-node Local AI Operations Tool that a technical operator can reproducibly run, use for real Local Ollama jobs, inspect job/result state, perform controlled recovery, audit/diagnose the system, preserve/restore bounded persistence, and cleanly hand off/tear down without requiring a cloud AI provider.`

## Acceptance Mapping
- reproducibly run / real Local Ollama jobs → frozen v1.0 UC-01/UC-02 plus M1 and latest exact-head Real Local AI Golden Path;
- inspect job/result state → M2 bounded read-only lifecycle console;
- controlled recovery / audit → frozen UC-04 plus M3;
- controlled service recovery → M4 Bifrost restart, M8 Kafka restart, M9 PostgreSQL same-volume restart;
- diagnose system → frozen observability boundary plus M7 diagnostic snapshot;
- preserve/restore bounded persistence → M6 one bounded PostgreSQL backup/restore case;
- handoff truth → M5 delivery handoff plus M10 truth reconciliation;
- clean teardown → M12 repository-owned retained-proof cleanup command;
- Local-first/no cloud requirement → frozen v1.0 routing boundary preserved throughout.

## Destination Decision
**DESTINATION REACHED — BOUNDED SINGLE-NODE TOOL.**

This is not a production-readiness claim. It does not establish enterprise security/identity, public production deployment, legal compliance certification, stable performance/cost, production SLA/SLO, HA/Kubernetes/multi-region, cloud-provider execution, generic autonomous operations, or DR/PITR/RPO-RTO beyond the specifically accepted bounded evidence.

No additional restart/cleanup/test permutation is justified merely to increase milestone count.

---

# 9. Current Post-v1.0 Progression Checkpoint

## Decision
- v1.0 remains **PASS / FREEZE / HUMAN REVIEW PASSED**;
- M1–M12 are **PASS / ACCEPTED / FROZEN**;
- M12 exact head `58c57c96c9c32049e6cf4df4d2149dafbc20e96f`, PR #54 merge `649207c81f1fecbfd251ba59ab55826117b722ff`, Issue #53 CLOSED / COMPLETED;
- exact-head M12 `33736638004`, M10 handoff truth `33736638010`, M5 delivery handoff `33736638012`, primary CI `33736638000`, Real Local AI Golden Path `33736638005`, and CI/CD `33736637997` are all SUCCESS;
- M12 artifact `9886113574` / `sha256:0313cef7765963493d890be046f23f3a7d1747af3037080a8f1e612c140b87b2` records the bounded cleanup evidence;
- review corrections are accepted: retained metadata is parsed as data rather than sourced, and recorded PIDs are ownership-checked before signaling;
- R-021 is CLOSED only for proof-owned retained-session cleanup;
- accepted evidence satisfies D1, so the authoritative product state is **DESTINATION REACHED — BOUNDED SINGLE-NODE TOOL**;
- no new micro-milestone is active.

## Exact Next Action
**Perform a D2 Destination Review before opening any new Issue. If justified, select one coherent `Versioned Single-node Delivery Candidate` milestone that reuses existing assets and proves a clean technical environment can follow a versioned/provenance-bearing acceptance path. Do not add another isolated restart/cleanup proof. If D2 cannot be bounded without a product/security decision, HOLD for human review instead.**
