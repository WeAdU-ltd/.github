#!/usr/bin/env python3
"""
WEA-24 — Smoke OAuth Gmail : refresh token → access token → profile (lecture) ;
  option --send : un message de test vers l'adresse du compte uniquement (envoi contrôlé).

Secrets (jamais dans le dépôt) : GMAIL_OAUTH_CLIENT_ID, GMAIL_OAUTH_CLIENT_SECRET,
  GMAIL_OAUTH_REFRESH_TOKEN — voir docs/GMAIL_AGENTS_WEA24.md

  --dry-run     Aucun réseau ; pour CI.

Variables optionnelles :
  GMAIL_OAUTH_SMOKE_SUBJECT, GMAIL_OAUTH_SMOKE_BODY — contenu du mail de test
  GMAIL_OAUTH_SMOKE_SEND=0 — refuse --send même si demandé
  GMAIL_OAUTH_ENV_FILE — chemin d'un fichier KEY=value (optionnel) ; ne remplit que les clés absentes
"""

from __future__ import annotations

import argparse
import base64
import email.message
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GMAIL_PROFILE_URL = "https://gmail.googleapis.com/gmail/v1/users/me/profile"
GMAIL_SEND_URL = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"


def load_optional_env_file(path: str) -> None:
    """Load KEY=value lines if file exists; do not override existing os.environ."""
    if not path or not os.path.isfile(path):
        return
    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.strip()
            if not key or key in os.environ:
                continue
            val = val.strip()
            if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
                val = val[1:-1]
            os.environ[key] = val


def post_form(url: str, fields: dict[str, str], timeout: float = 30.0) -> tuple[int, bytes]:
    data = urllib.parse.urlencode(fields).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.status, resp.read()


def request_json(
    url: str,
    method: str,
    headers: dict[str, str],
    body: bytes | None = None,
    timeout: float = 30.0,
) -> tuple[int, dict]:
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            status = resp.status
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code} {e.reason}: {err[:4000]}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Request failed: {e.reason}") from e
    try:
        return status, json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON: {e}") from e


def refresh_access_token(client_id: str, client_secret: str, refresh_token: str) -> str:
    status, raw = post_form(
        GOOGLE_TOKEN_URL,
        {
            "grant_type": "refresh_token",
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
        },
    )
    if status != 200:
        raise RuntimeError(f"Token endpoint status {status}: {raw[:2000]!r}")
    data = json.loads(raw.decode("utf-8"))
    token = data.get("access_token")
    if not token or not isinstance(token, str):
        raise RuntimeError("No access_token in token response")
    return token


def fetch_profile(access_token: str) -> dict:
    _, data = request_json(
        GMAIL_PROFILE_URL,
        "GET",
        {"Authorization": f"Bearer {access_token}"},
    )
    return data


def build_rfc822_to_self(from_addr: str, subject: str, body: str) -> str:
    msg = email.message.EmailMessage()
    msg["To"] = from_addr
    msg["Subject"] = subject
    msg.set_content(body)
    return msg.as_string()


def send_self_test(access_token: str, to_email: str) -> None:
    subject = (
        os.environ.get("GMAIL_OAUTH_SMOKE_SUBJECT", "").strip()
        or "WEA-24 Gmail OAuth smoke (agents)"
    )
    body = (
        os.environ.get("GMAIL_OAUTH_SMOKE_BODY", "").strip()
        or "Message de test automatisé (WeAdU agents). Vous pouvez supprimer ce message."
    )
    raw_bytes = build_rfc822_to_self(to_email, subject, body).encode("utf-8")
    raw_b64 = base64.urlsafe_b64encode(raw_bytes).decode("ascii")
    payload = json.dumps({"raw": raw_b64}).encode("utf-8")
    status, _ = request_json(
        GMAIL_SEND_URL,
        "POST",
        {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        body=payload,
    )
    if status != 200:
        raise RuntimeError(f"messages.send unexpected status {status}")


def run_dry_run() -> int:
    print("gmail_oauth_smoke_wea24: dry-run OK (no network).")
    print(
        "Live: set GMAIL_OAUTH_CLIENT_ID, GMAIL_OAUTH_CLIENT_SECRET, GMAIL_OAUTH_REFRESH_TOKEN; "
        "python3 scripts/gmail_oauth_smoke_wea24.py [--send]"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="WEA-24 Gmail OAuth smoke (read + optional self-send).")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Skip network; for CI.",
    )
    parser.add_argument(
        "--send",
        action="store_true",
        help="Send one test message to the mailbox itself only (controlled send).",
    )
    args = parser.parse_args()

    if args.dry_run:
        return run_dry_run()

    env_file = os.environ.get("GMAIL_OAUTH_ENV_FILE", "").strip()
    if env_file:
        load_optional_env_file(env_file)

    client_id = os.environ.get("GMAIL_OAUTH_CLIENT_ID", "").strip()
    client_secret = os.environ.get("GMAIL_OAUTH_CLIENT_SECRET", "").strip()
    refresh_token = os.environ.get("GMAIL_OAUTH_REFRESH_TOKEN", "").strip()

    if not client_id or not client_secret or not refresh_token:
        print(
            "Missing GMAIL_OAUTH_CLIENT_ID, GMAIL_OAUTH_CLIENT_SECRET, and/or GMAIL_OAUTH_REFRESH_TOKEN.\n"
            "Set them from GitHub/Cursor secrets (never commit). See docs/GMAIL_AGENTS_WEA24.md",
            file=sys.stderr,
        )
        return 2

    if args.send and os.environ.get("GMAIL_OAUTH_SMOKE_SEND", "1").strip() in ("0", "false", "no"):
        print("Send disabled by GMAIL_OAUTH_SMOKE_SEND=0.", file=sys.stderr)
        return 2

    try:
        access = refresh_access_token(client_id, client_secret, refresh_token)
        profile = fetch_profile(access)
    except RuntimeError as e:
        print(str(e), file=sys.stderr)
        return 1

    email_addr = profile.get("emailAddress")
    messages_total = profile.get("messagesTotal")
    print(
        f"OK: Gmail profile read; emailAddress={email_addr!r}; messagesTotal={messages_total!r}"
    )

    if args.send:
        if not email_addr or not isinstance(email_addr, str):
            print("Cannot send: profile has no emailAddress.", file=sys.stderr)
            return 1
        try:
            send_self_test(access, email_addr)
        except RuntimeError as e:
            print(str(e), file=sys.stderr)
            return 1
        print(f"OK: sent one test message to self ({email_addr!r}) only.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
