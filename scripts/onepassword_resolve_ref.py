#!/usr/bin/env python3
"""
Resolve a 1Password secret reference via the official Python SDK (no `op` CLI).

Uses OP_SERVICE_ACCOUNT_TOKEN (same as Cursor Cloud Agents). Never prints the secret
unless --print-value is passed (avoid in CI/logs).

Usage:
  export OP_SERVICE_ACCOUNT_TOKEN=…   # from Cursor secrets / env
  python3 scripts/onepassword_resolve_ref.py op://Vault/Item/field

  python3 scripts/onepassword_resolve_ref.py --dry-run

Requires: pip install -r requirements-onepassword.txt
Docs: https://github.com/1Password/onepassword-sdk-python
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys


async def _resolve(ref: str, print_value: bool) -> int:
    try:
        from onepassword.client import Client
    except ImportError:
        print(
            "Missing package: pip install -r requirements-onepassword.txt",
            file=sys.stderr,
        )
        return 2

    token = os.environ.get("OP_SERVICE_ACCOUNT_TOKEN", "").strip()
    if not token:
        print(
            "Missing OP_SERVICE_ACCOUNT_TOKEN.",
            file=sys.stderr,
        )
        return 2

    client = await Client.authenticate(
        auth=token,
        integration_name="WeAdU-agents",
        integration_version="1.0.0",
    )
    value = await client.secrets.resolve(ref)
    if print_value:
        sys.stdout.write(str(value))
        if not str(value).endswith("\n"):
            sys.stdout.write("\n")
    else:
        print("OK: secret resolved (length hidden). Use --print-value only in trusted terminals.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve op:// reference via 1Password SDK.")
    parser.add_argument(
        "ref",
        nargs="?",
        default="",
        help="Secret reference op://Vault/Item/field",
    )
    parser.add_argument(
        "--print-value",
        action="store_true",
        help="Print resolved secret (unsafe in logs)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Exit 0 without SDK if no token (CI)",
    )
    args = parser.parse_args()

    if args.dry_run:
        if os.environ.get("OP_SERVICE_ACCOUNT_TOKEN", "").strip():
            print("dry-run: OP_SERVICE_ACCOUNT_TOKEN is set; skipping SDK call.")
        else:
            print("dry-run: OP_SERVICE_ACCOUNT_TOKEN not set; skipping SDK call.")
        return 0

    ref = (args.ref or os.environ.get("OP_SECRET_REF", "")).strip()
    if not ref or not ref.startswith("op://"):
        print(
            "Provide op://Vault/Item/field as argument or OP_SECRET_REF.",
            file=sys.stderr,
        )
        return 2

    return asyncio.run(_resolve(ref, args.print_value))


if __name__ == "__main__":
    raise SystemExit(main())
