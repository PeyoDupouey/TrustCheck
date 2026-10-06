"""API HTTP locale minimale pour l'extension TrustCheck."""

from __future__ import annotations

import json
import os
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .analyzer import analyze_text
from .llm import OllamaFactChecker
from .sources import SearxngSourceProvider, StaticSourceProvider


class TrustCheckHandler(BaseHTTPRequestHandler):
    provider = None
    judge = None

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:  # noqa: N802 - nom imposé par http.server
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self) -> None:  # noqa: N802 - nom imposé par http.server
        if self.path != "/analyze":
            self._send_json(404, {"error": "route inconnue"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length))
            text = str(payload.get("text", "")).strip()[:12000]
            if not text:
                self._send_json(400, {"error": "text est requis"})
                return
            analysis = analyze_text(text, self.provider, self.judge, max_claims=3)
            self._send_json(200, asdict(analysis))
        except (ValueError, TypeError, json.JSONDecodeError) as error:
            self._send_json(400, {"error": f"requête invalide : {error}"})
        except (OSError, TimeoutError) as error:
            self._send_json(503, {"error": f"service indisponible : {error}"})

    def log_message(self, format: str, *args: object) -> None:
        print(f"[TrustCheck] {format % args}")


def main() -> None:
    searxng_url = os.getenv("TRUSTCHECK_SEARXNG_URL")
    ollama_url = os.getenv("TRUSTCHECK_OLLAMA_URL")
    TrustCheckHandler.provider = SearxngSourceProvider(searxng_url) if searxng_url else StaticSourceProvider()
    TrustCheckHandler.judge = (
        OllamaFactChecker(ollama_url, os.getenv("TRUSTCHECK_OLLAMA_MODEL", "qwen2.5:0.5b"))
        if ollama_url
        else None
    )
    server = ThreadingHTTPServer(("127.0.0.1", int(os.getenv("TRUSTCHECK_PORT", "8765"))), TrustCheckHandler)
    print(f"TrustCheck API locale : http://127.0.0.1:{server.server_port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
