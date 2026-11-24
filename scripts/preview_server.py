#!/usr/bin/env python3
import os
import mimetypes
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WWW_DIR = os.path.join(APP_DIR, "android", "assets", "www")
APK_CANDIDATES = [
    os.path.join(APP_DIR, "build", "Ramayana_Epic.apk"),
    "/home/user/Ramayana_Epic.apk",
]

mimetypes.add_type("application/vnd.android.package-archive", ".apk")
mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("audio/mpeg", ".mp3")


class RamayanaHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WWW_DIR, **kwargs)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def do_GET(self):
        clean_path = self.path.split("?", 1)[0]
        if clean_path == "/Ramayana_Epic.apk":
            apk_path = next((p for p in APK_CANDIDATES if os.path.exists(p)), None)
            if not apk_path:
                self.send_error(404, "APK not found")
                return
            size = os.path.getsize(apk_path)
            self.send_response(200)
            self.send_header("Content-Type", "application/vnd.android.package-archive")
            self.send_header("Content-Disposition", 'attachment; filename="Ramayana_Epic.apk"')
            self.send_header("Content-Length", str(size))
            self.end_headers()
            with open(apk_path, "rb") as f:
                while True:
                    chunk = f.read(65536)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
            return
        super().do_GET()

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", 8080), RamayanaHandler)
    print("Sri Ramayana preview server listening on http://0.0.0.0:8080", flush=True)
    server.serve_forever()
