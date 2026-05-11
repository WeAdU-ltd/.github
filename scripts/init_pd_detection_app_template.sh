#!/usr/bin/env bash
# WEA-131 — Copy pd-detection app template (socle WEA-35 + Python minimal + CI) into a target directory.
# Usage: from WeAdU-ltd/.github clone: bash scripts/init_pd_detection_app_template.sh [options] /path/to/pd-detection

set -euo pipefail

usage() {
  cat <<'EOF'
init_pd_detection_app_template.sh — Gabarit dépôt pd-detection (WEA-131)

Usage:
  bash scripts/init_pd_detection_app_template.sh [options] TARGET_DIR

Options:
  --dry-run   Print source and target; do not write files
  --force     Allow non-empty TARGET_DIR (overlay copy; may overwrite same paths)
  -h, --help  This message

Requires: run from a clone of WeAdU-ltd/.github (resolves templates/pd-detection-app).
EOF
}

dry_run=0
force=0
positional=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) dry_run=1 ;;
    --force) force=1 ;;
    -h|--help) usage; exit 0 ;;
    --) shift; positional+=("$@"); break ;;
    -*)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
    *) positional+=("$1") ;;
  esac
  shift || true
done

if [[ ${#positional[@]} -ne 1 ]]; then
  echo "Error: exactly one TARGET_DIR required." >&2
  usage >&2
  exit 2
fi

target="${positional[0]}"
here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
repo_root=$(cd "$here/.." && pwd)
src="$repo_root/templates/pd-detection-app"

if [[ ! -d "$src" ]]; then
  echo "Error: template directory not found: $src" >&2
  exit 1
fi

if [[ "$dry_run" -eq 1 ]]; then
  echo "Dry-run: would copy from $src to $target"
  exit 0
fi

mkdir -p "$target"
if [[ "$force" -eq 0 ]]; then
  if find "$target" -mindepth 1 -maxdepth 1 2>/dev/null | grep -q .; then
    echo "Error: TARGET_DIR is not empty: $target (use --force to overlay)" >&2
    exit 2
  fi
fi

cp -a "$src/." "$target/"
echo "Copied pd-detection template to: $target"
echo "Next: cd \"$target\" && python3 -m venv .venv && . .venv/bin/activate && pip install -e '.[dev]' && python3 -m pytest -q"
