"""Minimal HTTP surface for CI and local smoke until Repl code is merged."""

from __future__ import annotations

from flask import Flask, jsonify

from pd_detection import __version__


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/health")
    def health():
        return jsonify(
            status="ok",
            service="pd-detection",
            version=__version__,
        ), 200

    return app
