#!/usr/bin/env bash
# WEA-35 — Copy minimal agent socle files into a new or existing repo directory.
# Usage: from WeAdU-ltd/.github clone: bash scripts/init_wea35_socle_template.sh [options] /path/to/target-repo

set -euo pipefail

usage() {
  cat <<'EOF'
init_wea35_socle_template.sh — WEA-35 minimal socle (GitHub + Cursor)

Usage:
  bash scripts/init_wea35_socle_template.sh [options] TARGET_DIR

Options:
  --dry-run   Print actions without writing files
  --force     Overwrite existing files that match the template basenames
  -h, --help  This message

Requires: run from a clone of WeAdU-ltd/.github (script resolves ../templates/wea35-socle-minimal).
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
src="$repo_root/templates/wea35-socle-minimal"

if [[ ! -d "$src" ]]; then
  echo "Error: template directory not found: $src" >&2
  exit 1
fi

if [[ "$dry_run" -eq 0 ]]; then
  mkdir -p "$target"
fi

copy_one() {
  local rel="$1"
  local from="$src/$rel"
  local to="$target/$rel"
  if [[ ! -e "$from" ]]; then
    echo "Error: missing template file: $from" >&2
    exit 1
  fi
  if [[ -e "$to" && "$force" -eq 0 ]]; then
    echo "Skip (exists): $to  (use --force to overwrite)"
    return 0
  fi
  if [[ "$dry_run" -eq 1 ]]; then
    echo "Would copy: $from -> $to"
    return 0
  fi
  mkdir -p "$(dirname "$to")"
  cp -f "$from" "$to"
  echo "Copied: $to"
}

echo "Template: $src"
echo "Target:   $target"

copy_one "AGENTS.md"
copy_one ".cursor/hooks.json"
copy_one ".gitignore"
copy_one ".pre-commit-config.yaml"
copy_one "README.md"

echo "Done. See docs/inventory/WEA-35-weadu-socle-v5-lab-template.md in WeAdU-ltd/.github for full audit."
