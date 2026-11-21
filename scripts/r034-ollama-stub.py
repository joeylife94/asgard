"""Loopback-only delayed Ollama fixture for the R-034 Kafka workflow."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import time


class Handler(BaseHTTPRequestHandler):
    def reply(self, body):
        data = json.dumps(body).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/api/tags":
            self.reply({"models": [{"name": "smollm:135m"}]})
        else:
            self.send_error(404)

    def do_POST(self):
        self.rfile.read(int(self.headers["Content-Length"]))
        if self.path == "/api/pull":
            self.reply({"status": "success"})
        elif self.path == "/api/generate":
            print("generate", flush=True)
            time.sleep(60)
            self.reply({"model": "smollm:135m", "done": True, "response": "## 요약\nSlow fixture result"})
        else:
            self.send_error(404)


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", 11434), Handler).serve_forever()
