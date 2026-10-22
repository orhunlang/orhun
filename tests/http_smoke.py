#!/usr/bin/env python3
"""HTTP client smoke: http.get/post/put/delete with headers on a local server."""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):  # noqa: A003
        return

    def _send(self, code: int, body: bytes, content_type: str = "text/plain"):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("X-Orhun-Test", "1")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802
        if self.path.startswith("/merhaba"):
            self._send(200, "merhaba-orhun".encode("utf-8"))
        elif self.path.startswith("/baslik"):
            payload = {
                "x-orhun": self.headers.get("X-Orhun", ""),
                "accept": self.headers.get("Accept", ""),
            }
            self._send(200, json.dumps(payload).encode("utf-8"), "application/json")
        elif self.path.startswith("/yok"):
            self._send(404, "bulunamadi".encode("utf-8"))
        else:
            self._send(200, "ok".encode("utf-8"))

    def do_POST(self):  # noqa: N802
        length = int(self.headers.get("Content-Length", "0") or "0")
        body = self.rfile.read(length) if length else b""
        payload = {
            "method": "POST",
            "path": self.path,
            "content_type": self.headers.get("Content-Type", ""),
            "body": body.decode("utf-8", errors="replace"),
        }
        self._send(201, json.dumps(payload).encode("utf-8"), "application/json")

    def do_PUT(self):  # noqa: N802
        length = int(self.headers.get("Content-Length", "0") or "0")
        body = self.rfile.read(length) if length else b""
        payload = {
            "method": "PUT",
            "body": body.decode("utf-8", errors="replace"),
        }
        self._send(200, json.dumps(payload).encode("utf-8"), "application/json")

    def do_DELETE(self):  # noqa: N802
        self._send(200, "silindi".encode("utf-8"))


def run_source(binary: Path, source: str) -> tuple[int, str]:
    with tempfile.TemporaryDirectory(prefix="orhun_http_") as tmp:
        path = Path(tmp) / "ornek.oh"
        path.write_text(source, encoding="utf-8")
        proc = subprocess.run(
            [str(binary), str(path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=20,
        )
        return proc.returncode, (proc.stdout + proc.stderr).replace("\r\n", "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="HTTP client smoke")
    parser.add_argument("binary", help="Orhun executable")
    args = parser.parse_args()
    binary = Path(args.binary)
    require(binary.exists(), f"Binary not found: {binary}")

    server = HTTPServer(("127.0.0.1", 0), Handler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{port}"
    try:
        cases = [
            (
                "get",
                f'''
yanit olsun http.get("{base}/merhaba")
yaz yanit.durum
yaz yanit.govde
yaz yanit.basliklar["X-Orhun-Test"]
''',
                ["200", "merhaba-orhun", "1"],
            ),
            (
                "get-headers",
                f'''
yanit olsun http.get("{base}/baslik", {{"Accept": "application/json", "X-Orhun": "evet"}})
yaz yanit.durum
yaz yanit.govde
''',
                ["200", "evet", "application/json"],
            ),
            (
                "post-json",
                f'''
govde olsun json.yaz({{"ad": "orhun"}})
yanit olsun http.post("{base}/yanki", govde, {{"Content-Type": "application/json"}})
yaz yanit.durum
yaz yanit.govde
''',
                ["201", "POST", "application/json", "orhun"],
            ),
            (
                "put",
                f'''
yanit olsun http.put("{base}/kaynak", "{{\\"ok\\":true}}", {{"Content-Type": "application/json"}})
yaz yanit.durum
yaz yanit.govde
''',
                ["200", "PUT"],
            ),
            (
                "delete",
                f'''
yanit olsun http.delete("{base}/kaynak")
yaz yanit.durum
yaz yanit.govde
''',
                ["200", "silindi"],
            ),
            (
                "not-found",
                f'''
yanit olsun http.get("{base}/yok")
yaz yanit.durum
yaz yanit.govde
''',
                ["404", "bulunamadi"],
            ),
            (
                "ag-alias",
                f'''
yanit olsun ag.get("{base}/merhaba")
yaz yanit.durum
yaz yanit.govde
''',
                ["200", "merhaba-orhun"],
            ),
            (
                "stdlib-wrap",
                f'''
http_istemci olsun dahil_et "orhun/http.oh"
yanit olsun http_istemci.get("{base}/merhaba")
yaz http_istemci.yanit_basari_mi(yanit)
yaz yanit.durum
''',
                ["1", "200"],
            ),
        ]

        for name, source, needles in cases:
            code, out = run_source(binary, source)
            require(code == 0, f"{name}: exit={code}\n{out}")
            for needle in needles:
                require(needle in out, f"{name}: missing {needle!r} in\n{out}")
            print(f"[OK] {name}")

        print("HTTP client smoke passed.")
        return 0
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    raise SystemExit(main())
