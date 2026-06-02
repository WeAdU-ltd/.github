#!/usr/bin/env python3
"""Upload WEA-28 multisite audit CSV to a new Google Sheet (service account)."""

from __future__ import annotations

import argparse
import asyncio
import csv
import json
import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

DEFAULT_CSV = _ROOT / "docs/inventory/WEA-28-agency-plus-multisites-2026-06.csv"
OP_REF_SA = "op://Replit/GOOGLE_SERVICE_ACCOUNT_JSON/credential"


async def _load_sa_json() -> dict:
    from onepassword.client import Client

    token = os.environ.get("OP_SERVICE_ACCOUNT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("Missing OP_SERVICE_ACCOUNT_TOKEN")
    client = await Client.authenticate(
        auth=token,
        integration_name="WeAdU-agents",
        integration_version="1.0.0",
    )
    raw = await client.secrets.resolve(OP_REF_SA)
    return json.loads(raw)


def upload(csv_path: Path, title: str, share_with: str | None) -> str:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    sa_info = asyncio.run(_load_sa_json())
    creds = service_account.Credentials.from_service_account_info(
        sa_info,
        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file"],
    )
    sheets = build("sheets", "v4", credentials=creds, cache_discovery=False)
    drive = build("drive", "v3", credentials=creds, cache_discovery=False)

    with csv_path.open(encoding="utf-8") as f:
        rows = list(csv.reader(f))
    if not rows:
        raise ValueError("empty csv")

    body = {
        "properties": {"title": title},
        "sheets": [{"properties": {"title": "Multisites OVH"}}],
    }
    created = sheets.spreadsheets().create(body=body).execute()
    sid = created["spreadsheetId"]
    sheets.spreadsheets().values().update(
        spreadsheetId=sid,
        range="Multisites OVH!A1",
        valueInputOption="RAW",
        body={"values": rows},
    ).execute()

    if share_with:
        drive.permissions().create(
            fileId=sid,
            body={"type": "user", "role": "writer", "emailAddress": share_with},
            sendNotificationEmail=False,
        ).execute()

    return f"https://docs.google.com/spreadsheets/d/{sid}/edit"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    p.add_argument("--title", default="WEA-28 OVH Agency Plus — 220 multisites (2026-06)")
    p.add_argument("--share", metavar="EMAIL", help="Grant writer access to this Google account")
    args = p.parse_args()
    try:
        url = upload(args.csv, args.title, args.share)
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    print(url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
