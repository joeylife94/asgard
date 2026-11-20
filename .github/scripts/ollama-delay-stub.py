#!/usr/bin/env python3
"""Synthetic Ollama stand-in with a fixed generation delay (R-034 proof).

Answers the few Ollama endpoints Asgard's local proof touches. /api/generate
sleeps STUB_DELAY_SECONDS before returning a fixed, obviously synthetic
analysis, and every generate call is recorded so a proof can count them via
GET /calls. This is NOT a model and produces no local-AI evidence.

Environment:
  PORT                 listen port (default 11434), bound to 127.0.0.1
  STUB_MODEL           model name advertised by /api/tags (default smollm:135m)
  STUB_DELAY_SECONDS   delay of /api/generate in seconds (default 60)
"""

import json
import os
import sys
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(os.environ.get("PORT", "11434"))
MODEL = os.environ.get("STUB_MODEL", "smollm:135m")
DELAY = float(os.environ.get("STUB_DELAY_SECONDS", "60"))

# Section format understood by Bifrost's _parse_analysis_response.
STUB_RESPONSE = (
    "## Summary\n"
    "This is a fixed synthetic analysis returned by the R-034 delayed Ollama stub. "
    "No model generated it.\n\n"
    "## Issue\n"
    "Stub response used to prove consumer liveness during a long generation.\n\n"
    "## Recommendation\n"
    "None. This text is a stub and carries no diagnostic value.\n"
)

_lock = threading.Lock()
_calls = []


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        sys.stderr.write("[ollama-delay-stub] %s %s\n" % (self.log_date_time_string(), fmt % args))
        sys.stderr.flush()

    def _send_json(self, status, body):
        data = json.dumps(body).encode("utf-8")
        try:
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            self.log_message("client disconnected before response was written")
            self.close_connection = True

    def _read_json(self):
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length > 0 else b""
        try:
            return json.loads(raw.decode("utf-8")) if raw else {}
        except ValueError:
            return {}

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/api/tags":
            self._send_json(200, {"models": [{"name": MODEL, "model": MODEL}]})
        elif path == "/api/version":
            self._send_json(200, {"version": "0.0.0-r034-stub"})
        elif path == "/":
            self._send_json(200, {"status": "Ollama delay stub (R-034)"})
        elif path == "/calls":
            with _lock:
                calls = [dict(c) for c in _calls]
            self._send_json(200, {"generate_calls": len(calls), "calls": calls})
        else:
            self._send_json(404, {"error": "not found: %s" % path})

    def do_POST(self):
        path = self.path.split("?", 1)[0]
        body = self._read_json()
        if path == "/api/pull":
            self._send_json(200, {"status": "success"})
        elif path == "/api/generate":
            record = {"started_at": _now(), "finished_at": None}
            with _lock:
                _calls.append(record)
            self.log_message("generate started, sleeping %ss", DELAY)
            time.sleep(DELAY)
            with _lock:
                record["finished_at"] = _now()
            self._send_json(200, {
                "model": body.get("model") or MODEL,
                "created_at": _now(),
                "response": STUB_RESPONSE,
                "done": True,
                "done_reason": "stop",
                "prompt_eval_count": 1,
                "eval_count": 1,
            })
        else:
            self._send_json(404, {"error": "not found: %s" % path})

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-Length", "0")
        self.end_headers()


class Server(ThreadingHTTPServer):
    daemon_threads = True

    def handle_error(self, request, client_address):
        # A client that gave up during the delay must not take the server down.
        sys.stderr.write("[ollama-delay-stub] connection error from %s: %s\n"
                         % (client_address, sys.exc_info()[1]))
        sys.stderr.flush()


def main():
    server = Server(("127.0.0.1", PORT), Handler)
    sys.stderr.write("[ollama-delay-stub] listening on 127.0.0.1:%d model=%s delay=%ss\n"
                     % (PORT, MODEL, DELAY))
    sys.stderr.flush()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
