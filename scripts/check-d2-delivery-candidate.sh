#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

required=(
  delivery/single-node-candidate/VERSION
  delivery/single-node-candidate/MANIFEST.md
  ASGARD_MASTER.md
  docs/SINGLE_NODE_HANDOFF.md
  scripts/local-proof.sh
  scripts/operator-diagnostic-snapshot.sh
  scripts/m6-backup-restore-proof.sh
  scripts/cleanup-retained-proof.sh
)
for path in "${required[@]}"; do
  test -s "$path" || { echo "missing required delivery file: $path" >&2; exit 1; }
done

version="$(tr -d '\r\n' < delivery/single-node-candidate/VERSION)"
[[ "$version" =~ ^asgard-single-node-d2-candidate-[0-9]+$ ]] || { echo "invalid candidate version: $version" >&2; exit 1; }

manifest=delivery/single-node-candidate/MANIFEST.md
handoff=docs/SINGLE_NODE_HANDOFF.md
for token in \
  'scripts/local-proof.sh' \
  'scripts/operator-diagnostic-snapshot.sh' \
  'scripts/m6-backup-restore-proof.sh' \
  'scripts/cleanup-retained-proof.sh' \
  'Production readiness is not verified.' \
  'Cloud-provider execution is not verified.' \
  'Enterprise identity/RBAC is not verified.'; do
  grep -Fq "$token" "$manifest" || { echo "manifest missing contract: $token" >&2; exit 1; }
done

grep -Fq 'DESTINATION REACHED — BOUNDED SINGLE-NODE TOOL' ASGARD_MASTER.md || { echo 'D1 acceptance missing from MASTER' >&2; exit 1; }
grep -Fq 'scripts/local-proof.sh' "$handoff"
grep -Fq 'scripts/cleanup-retained-proof.sh' "$handoff"

bash -n scripts/local-proof.sh
bash -n scripts/operator-diagnostic-snapshot.sh
bash -n scripts/m6-backup-restore-proof.sh
bash -n scripts/cleanup-retained-proof.sh

echo "D2 delivery candidate contract PASS: $version"
