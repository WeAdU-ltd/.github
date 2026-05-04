#!/usr/bin/env bash
# Sync .cursorrules from this repository root to one or more target project directories.
# Usage: /absolute/path/to/repo/tools/sync_cursorrules.sh /path/to/other/project [/path/to/another ...]
set -euo pipefail
export LC_ALL=C.UTF-8

if [[ $# -lt 1 ]]; then
  echo "usage: $0 <target_dir> [<target_dir> ...]" >&2
  echo "  Copies .cursorrules from the repository containing this script to each target directory." >&2
  exit 2
fi

_script_path=$(readlink -f "${BASH_SOURCE[0]}")
_script_dir=$(dirname "${_script_path}")
_repo_root=$(dirname "${_script_dir}")
_src="${_repo_root}/.cursorrules"

if [[ ! -f "${_src}" ]]; then
  echo "error: source file not found: ${_src}" >&2
  exit 1
fi

_status=0
for _raw in "$@"; do
  if [[ -z "${_raw}" ]]; then
    echo "error: empty target path in argument list" >&2
    _status=1
    continue
  fi
  _target=$(readlink -f "${_raw}" 2>/dev/null || true)
  if [[ -z "${_target}" || ! -d "${_target}" ]]; then
    echo "error: target is not an existing directory: ${_raw}" >&2
    _status=1
    continue
  fi
  if [[ "${_target}" == "${_repo_root}" ]]; then
    echo "skipped: target is the source repository root (already canonical): ${_target}"
    continue
  fi
  _dest="${_target}/.cursorrules"
  cp -- "${_src}" "${_dest}"
  echo "updated: ${_dest}"
done

exit "${_status}"
