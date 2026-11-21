#!/usr/bin/env bash
set -euo pipefail
if [[ $# -lt 2 || $# -gt 3 ]]; then
  echo "Usage: Scripts/reproduce.sh <MoneyData-xlsx> <explainable-offers-research-v1.0.0-root> [results-dir]" >&2
  exit 64
fi
XLSX="$1"
PROJECT_ROOT="$2"
RESULTS_DIR="${3:-$(cd "$(dirname "$0")/.." && pwd)/Results}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$RESULTS_DIR"
exec > >(tee "$RESULTS_DIR/reproduction.log") 2>&1
PYTHON_BIN="${PYTHON_BIN:-python3}"
WORK_DIR="$(mktemp -d "${TMPDIR:-/tmp}/offers-external.XXXXXX")"
trap 'rm -rf "$WORK_DIR"' EXIT

# Require the official v1.0.0 checkout and compare every copied classifier file.
SOURCE_TAG="$(git -C "$PROJECT_ROOT" describe --tags --exact-match HEAD 2>/dev/null || true)"
if [[ "$SOURCE_TAG" != "v1.0.0" ]]; then
  echo "Expected original repository checkout at tag v1.0.0; found '${SOURCE_TAG:-no exact tag}'." >&2
  exit 2
fi
SOURCE_COMMIT="$(git -C "$PROJECT_ROOT" rev-parse HEAD)"
printf 'original_source_tag=%s\noriginal_source_commit=%s\n' "$SOURCE_TAG" "$SOURCE_COMMIT"
for source_file in Classifier.swift ConflictAware.swift Models.swift Profile.swift Ranking.swift Tokenizer.swift; do
  if ! cmp -s "$ROOT/Sources/OfferCore/$source_file" \
      "$PROJECT_ROOT/artifact/Validation/Sources/OfferCore/$source_file"; then
    echo "Classifier source mismatch for $source_file; refusing to evaluate." >&2
    exit 3
  fi
done
echo "Original v1.0.0 classifier source comparison: PASS (6 files byte-identical)."

CATALOG="$PROJECT_ROOT/artifact/Sources/SyntheticData/Resources/catalog.json"
"$PYTHON_BIN" "$ROOT/Scripts/prepare_dataset.py" --xlsx "$XLSX" --catalog "$CATALOG" \
  --records-out "$WORK_DIR/mapped.tsv" --summary-out "$RESULTS_DIR/dataset-summary.json"
mkdir -p "$WORK_DIR/clang-module-cache" "$WORK_DIR/swift-module-cache"
(cd "$ROOT" && CLANG_MODULE_CACHE_PATH="$WORK_DIR/clang-module-cache" SWIFT_MODULE_CACHE_PATH="$WORK_DIR/swift-module-cache" \
  swift run --scratch-path "$WORK_DIR/swiftpm" -c release external-evaluation "$WORK_DIR/mapped.tsv" "$RESULTS_DIR")
"$PYTHON_BIN" "$ROOT/Scripts/audit_results.py" --results "$RESULTS_DIR" \
  --dataset-summary "$RESULTS_DIR/dataset-summary.json" --log "$RESULTS_DIR/audit.log"
