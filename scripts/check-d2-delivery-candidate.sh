#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

required=(
  delivery/single-node-candidate/VERSION
  delivery/single-node-candidate/MANIFEST.md
  delivery/single-node-candidate/PILOT_CONFIG.example
  ASGARD_MASTER.md
  docs/SINGLE_NODE_HANDOFF.md
  docker-compose.pilot.yml
  scripts/pilot-configured.sh
  scripts/pilot-release.sh
  scripts/pilot.sh
  scripts/local-proof.sh
  scripts/operator-diagnostic-snapshot.sh
  scripts/m6-backup-restore-proof.sh
  scripts/cleanup-retained-proof.sh
)
for path in "${required[@]}"; do
  test -s "$path" || { echo "missing required delivery file: $path" >&2; exit 1; }
done

version="$(tr -d '\r\n' < delivery/single-node-candidate/VERSION)"
case "$version" in
  asgard-single-node-d2-candidate-[0-9]*|asgard-single-node-d4-compatible-[0-9]*|asgard-single-node-d5-config-[0-9]*) ;;
  *) echo "invalid candidate version: $version" >&2; exit 1 ;;
esac
[[ "$version" =~ ^asgard-single-node-(d2-candidate|d4-compatible|d5-config)-[0-9]+$ ]] || { echo "invalid candidate version: $version" >&2; exit 1; }

manifest=delivery/single-node-candidate/MANIFEST.md
handoff=docs/SINGLE_NODE_HANDOFF.md
for token in \
  'scripts/pilot.sh' \
  'bash scripts/pilot.sh validate' \
  'bash scripts/pilot.sh start' \
  'bash scripts/pilot.sh stop' \
  'bash scripts/pilot.sh purge' \
  'scripts/local-proof.sh' \
  'scripts/operator-diagnostic-snapshot.sh' \
  'scripts/m6-backup-restore-proof.sh' \
  'scripts/cleanup-retained-proof.sh' \
  'Production readiness is not verified.' \
  'Cloud-provider execution is not verified.' \
  'Enterprise identity/RBAC is not verified.' \
  'Version upgrade/rollback is not verified.'; do
  grep -Fq "$token" "$manifest" || { echo "manifest missing contract: $token" >&2; exit 1; }
done

grep -Fq 'DESTINATION REACHED — BOUNDED SINGLE-NODE TOOL' ASGARD_MASTER.md || { echo 'D1 acceptance missing from MASTER' >&2; exit 1; }
grep -Fq 'D3-01 — ACCEPTED' ASGARD_MASTER.md || { echo 'D3-01 acceptance missing from MASTER' >&2; exit 1; }
grep -Fq 'DESTINATION REACHED — BOUNDED VERSIONED UPGRADE / ROLLBACK PILOT' ASGARD_MASTER.md || { echo 'D4 acceptance missing from MASTER' >&2; exit 1; }
for token in \
  'scripts/pilot.sh' \
  'persistence-preserving' \
  'scripts/m6-backup-restore-proof.sh' \
  'scripts/operator-diagnostic-snapshot.sh' \
  'Production readiness is not verified.'; do
  grep -Fq "$token" "$handoff" || { echo "handoff missing persistent pilot contract: $token" >&2; exit 1; }
done

bash -n scripts/pilot-configured.sh
bash -n scripts/pilot-release.sh
bash -n scripts/pilot.sh
bash -n scripts/local-proof.sh
bash -n scripts/operator-diagnostic-snapshot.sh
bash -n scripts/m6-backup-restore-proof.sh
bash -n scripts/cleanup-retained-proof.sh

echo "D2/D3/D4/D5 delivery candidate contract PASS: $version"