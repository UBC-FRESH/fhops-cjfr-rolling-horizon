#!/usr/bin/env bash
# Build conceptual (TikZ) figures into manuscript/figures/. Data figures come from analyze_rerun.py.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TECTONIC="${TECTONIC:-tectonic}"
for src in "$ROOT"/manuscript/figures/src/*.tex; do
  "$TECTONIC" -o "$ROOT/manuscript/figures" "$src"
done
