"""Development server entrypoint (replaces `python main.py` style Replit runs)."""

from __future__ import annotations

import argparse
import os

from pd_detection.app import create_app


def main() -> None:
    parser = argparse.ArgumentParser(description="pd-detection Flask dev server")
    parser.add_argument(
        "--host",
        default=os.environ.get("PD_DETECTION_HOST", "127.0.0.1"),
        help="Bind address (default 127.0.0.1 or PD_DETECTION_HOST)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("PD_DETECTION_PORT", "5000")),
        help="TCP port (default 5000 or PD_DETECTION_PORT)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Flask debug (do not use in production)",
    )
    args = parser.parse_args()
    app = create_app()
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
