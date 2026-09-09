# ASGARD MASTER

> **Authoritative execution and progression contract**
>
> Single source of truth for the frozen Asgard v1.0 Proof baseline and bounded post-v1.0 progression. Current repository / Issue / PR / executable evidence overrides README claims, historical roadmap text, old portfolio positioning, Scheduled Task prompt text, and agent self-report.

## 0. Control

- **Frozen Baseline**: Asgard v1.0 — Wishket / Freelance Proof
- **Frozen Baseline Level**: READY TO SHOW bounded software Proof
- **Frozen v1.0 Product Direction**: **Local-first AI Operations Platform**
- **Accepted Product Destinations**: **D1 — Bounded Single-node Tool / D2 — Versioned Single-node Delivery Candidate / D3 — Bounded Single-node Pilot Deployment**
- **Current Product Destination**: **D4 — Bounded Versioned Upgrade / Rollback Pilot — ACTIVE**
- **Current Phase**: **D4-02 — COMPATIBLE A→B RELEASE TRANSITION — ACTIVE**
- **Current Batch**: **D4-02 / Issue #65**
- **Current Status**: **v1.0 FROZEN / M1–M12 FROZEN / D1+D2+D3 ACCEPTED / FROZEN / D4 ACTIVE / D4-01 ACCEPTED**
- **Repo**: `joeylife94/asgard`
- **Branch**: `main`
- **Accepted D4-01 exact PR head**: `e1087697014a2ce0416349998eb3e65216a45cb7`
- **Accepted D4-01 merge main SHA**: `209b7522cfbfb8668029dca6a2c84b744ef5f98a`
- **Active Implementation Issue**: #65 — D4-02: execute compatible A→B release transition on shared pilot state
- **Active Implementation PR**: pending
- **Selected Next Milestone**: D4-02 — compatible same-schema A→B release transition on shared pilot state
- **Human Review Decision**: **2026-09-09 — D4 Bounded Versioned Upgrade / Rollback Pilot selected; D5 Operator-owned Configuration Pilot and D6 Bounded Maintenance & Recovery Pilot pre-authorized after destination-level acceptance**
- **Updated**: 2026-09-09
- **Final v1.0 Gate**: **PASS — FREEZE APPROVED**
- **Post-v1.0 Gate**: **M1–M12 PASS / ACCEPTED / FROZEN; D1+D2+D3 DESTINATIONS ACCEPTED / FROZEN; D4 ACTIVE / D4-01 ACCEPTED / D4-02 ISSUE #65**

---

# 1. Product Definition

**Asgard는 운영 로그와 이벤트를 영속적인 비동기 Job으로 처리하고, Kafka 기반 실행 흐름과 Local LLM 분석, 결과 저장, 실패 복구, 감사 및 관측 기능을 제공하는 Local-first AI Operations Platform이다.**

Asgard v1.0 and D1/D2/D3 accepted slices remain frozen. D4 may add only compatible same-schema version-transition ownership/evidence without upgrading production, enterprise, cloud, HA, SLA/SLO, schema-migration, systemd, unattended-operation, or general rollback claims.

---

# 2. Frozen v1.0 Boundary

The accepted v1.0 boundary remains frozen: Heimdall/Bifrost, PostgreSQL/Kafka, Local Ollama, persistent Analysis Job lifecycle, result persistence/idempotency, fail-closed Local-first routing, bounded DLQ/redrive/audit, bounded observability and executable CI/E2E evidence. Historical cloud code may remain but is not an accepted requirement or claim.

Explicitly deferred remain AWS/Bedrock/OIDC/cloud execution, Kubernetes/HA/multi-node, enterprise identity/RBAC/SSO, production SLA/SLO, security/legal certification, systemd/automatic boot, unattended operation, and cross-schema migration/rollback.

---

# 3. Accepted Evidence

All previously recorded v1.0 M1–M12, D1, D2 and D3 exact-head executable evidence remains ACCEPTED / FROZEN and is not rewritten by D4.

### D4-01 — Release-independent Pilot Ownership — ACCEPTED

- Issue #63: CLOSED / COMPLETED.
- Accepted exact PR head: `e1087697014a2ce0416349998eb3e65216a45cb7`.
- Merge main SHA: `209b7522cfbfb8668029dca6a2c84b744ef5f98a`.
- Exact-head executable gates: D4-01 acceptance plus relevant D3-01, D3-03, D2 candidate/provenance, Real Local AI, primary CI and CI/CD were GREEN before merge.
- Accepted behavior: explicit release-independent pilot home/state boundary; truthful VERSION/commit/root provenance; existing D3 persistent Local-first lifecycle retained; `stop` persistence-preserving; `purge` explicit/destructive; conflicting/stale release ownership fails closed.
- Non-claims: D4-01 does **not** establish general upgrade/rollback, schema migration, production readiness, HA/DR, SLA/SLO, systemd/unattended operation, cloud execution, RBAC/SSO, or compliance.

---

# 4. Known Risks / Holds

Previously accepted/frozen risks and closures remain authoritative historical evidence.

- **R-025 — CLOSED**: D3 pilot state/ownership was coupled to one extracted release root. Closed by accepted D4-01 release-independent pilot-home/provenance/conflict evidence.
- **R-026 — ACTIVE**: no executable evidence yet demonstrates a compatible same-schema candidate A→B transition over the same explicit pilot-owned persistent state while preserving the A Job/result, accepting new B Local-first work, and truthfully changing release provenance. Handle only through D4-02 / Issue #65.

---

# 5. Work Item / PR Lifecycle

1. MASTER first on the Issue-linked branch.
2. Current repository / Issue / PR / executed evidence overrides stale checkpoint text and scheduled-task self-report.
3. One bounded Issue → one bounded PR → exact-head executable acceptance/review → expected-head protected merge → Issue close → current-main MASTER reconciliation → Destination Review.
4. Technical RED/HOLD is a correction state, not termination. Same-gap corrections remain in the same PR.
5. Do not manufacture reliability permutations or proof-of-proof work after an invariant is accepted.

---

# 6. Current Destination — D4

## D4 — Bounded Versioned Upgrade / Rollback Pilot — ACTIVE

Goal: compatible versioned candidates can deliberately take ownership of the same explicit single-node pilot persistence/state boundary, preserve prior Job/results, perform new Local-first work, and expose truthful release provenance. This does not imply schema migration or production-grade rollback.

### D4-01 — ACCEPTED / FROZEN

Release-independent pilot ownership is established by the accepted evidence above.

### D4-02 — ACTIVE / Issue #65

Smallest remaining demonstrated blocker: execute one SAME-SCHEMA / BACKWARD-COMPATIBLE candidate A→B transition using the accepted D4-01 pilot-home ownership surface and existing D2/D3 assets.

Required exact-head acceptance:

1. A and B are explicitly identified compatible same-schema candidates.
2. A starts on an explicit shared pilot home, executes one real Local Ollama Analysis Job, and persists an inspectable Job/result.
3. A performs a persistence-preserving controlled stop/transition.
4. B takes ownership of the same pilot home/state boundary and records truthful VERSION/commit/root provenance.
5. The A-created Job/result remains inspectable under B.
6. B executes and persists a new real Local Ollama Analysis Job successfully.
7. Relevant D4-01/D3/D2 regression/provenance gates remain GREEN.
8. No production/public deployment, HA/multi-node, cloud execution, RBAC/SSO, SLA/SLO, DR/PITR/RPO/RTO, systemd/unattended operation, compliance, schema-migration, or general rollback guarantee is added.

Rollback remains conditional. Do not create B→A merely as another permutation; decide only after D4-02 destination review.

---

# 7. Pre-authorized Continuation

After D4 is explicitly DESTINATION REACHED and reconciled, automatically select D5 — Operator-owned Configuration Pilot. After D5 acceptance/reconciliation, automatically select D6 — Bounded Maintenance & Recovery Pilot. D7 and any systemd/automatic boot, unattended operation, Kubernetes/HA/multi-node, replication/multi-broker, cloud execution, enterprise identity/RBAC/SSO, public/production deployment, SLA/SLO, or certification direction requires Human Review.
