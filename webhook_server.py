#!/usr/bin/env python3
"""
Standalone webhook server for GitHub CI/CD deployment
Run this outside of Docker on the host machine
"""

import os
import subprocess
import hmac
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', '')
PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
PORT = 9000


class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != '/deploy':
            self.send_error(404)
            return

        # Check secret
        secret = self.headers.get('X-Webhook-Secret', '')
        if not WEBHOOK_SECRET or not hmac.compare_digest(secret, WEBHOOK_SECRET):
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b'{"error": "Invalid secret"}')
            return

        try:
            # Pull latest code
            result = subprocess.run(
                ['git', 'pull', 'origin', 'main'],
                cwd=PROJECT_PATH,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({
                    'status': 'error',
                    'message': 'Git pull failed',
                    'stderr': result.stderr
                }).encode())
                return

            # Rebuild and restart Docker
            rebuild = subprocess.run(
                ['docker', 'compose', 'up', '-d', '--build'],
                cwd=PROJECT_PATH,
                capture_output=True,
                text=True,
                timeout=300
            )

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'status': 'success',
                'git_output': result.stdout,
                'docker_output': rebuild.stdout
            }).encode())

        except subprocess.TimeoutExpired:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b'{"error": "Command timeout"}')
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def log_message(self, format, *args):
        print(f"[Webhook] {args[0]}")


if __name__ == '__main__':
    if not WEBHOOK_SECRET:
        print("ERROR: WEBHOOK_SECRET environment variable not set")
        exit(1)

    server = HTTPServer(('127.0.0.1', PORT), WebhookHandler)
    print(f"Webhook server running on http://127.0.0.1:{PORT}")
    server.serve_forever()
