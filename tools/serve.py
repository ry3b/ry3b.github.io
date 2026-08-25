#!/usr/bin/env python3
"""Local editor for data/cv.json, bound to localhost only.

    python3 tools/serve.py           http://127.0.0.1:8000/_editor

The same server also previews the site at http://127.0.0.1:8000/, so the
generated pages can be checked right after a build.
"""
import json
import os
import subprocess
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "cv.json")
EDITOR = os.path.join(ROOT, "tools", "editor.html")


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def _send(self, code, body, ctype="application/json"):
        body = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.rstrip("/") == "/_editor":
            with open(EDITOR, "rb") as fh:
                return self._send(200, fh.read(), "text/html; charset=utf-8")
        if self.path == "/_data":
            with open(DATA, "rb") as fh:
                return self._send(200, fh.read())
        return super().do_GET()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length).decode()

        if self.path == "/_data":
            try:
                data = json.loads(raw)
            except json.JSONDecodeError as exc:
                return self._send(400, json.dumps({"error": "not valid JSON: %s" % exc}))
            # write to a temp file first: a crash mid-write must not destroy the CV
            tmp = DATA + ".tmp"
            with open(tmp, "w") as fh:
                json.dump(data, fh, indent=2, ensure_ascii=False)
                fh.write("\n")
            os.replace(tmp, DATA)
            return self._send(200, json.dumps({"saved": True}))

        if self.path == "/_build":
            proc = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "build.py")],
                                  cwd=ROOT, capture_output=True, text=True)
            return self._send(200, json.dumps({
                "ok": proc.returncode == 0,
                "log": (proc.stdout + proc.stderr).strip(),
            }))

        return self._send(404, json.dumps({"error": "no such endpoint"}))

    def log_message(self, fmt, *args):
        if not self.path.startswith(("/_data", "/style.css", "/images")):
            sys.stderr.write("  %s\n" % (fmt % args))


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print("editor:  http://127.0.0.1:%d/_editor" % port)
    print("site:    http://127.0.0.1:%d/" % port)
    print("ctrl-c to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
        server.shutdown()
