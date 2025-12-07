"""
Webhook endpoint for automated deployment
"""

import os
import subprocess
import hmac
import hashlib
from flask import Blueprint, request, jsonify
from app import csrf

webhook_bp = Blueprint('webhook', __name__)

WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', '')
PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def verify_secret(request):
    """Verify the webhook secret"""
    secret = request.headers.get('X-Webhook-Secret', '')
    return hmac.compare_digest(secret, WEBHOOK_SECRET)


@webhook_bp.route('/deploy', methods=['POST'])
@csrf.exempt
def deploy():
    """Handle deployment webhook"""
    if not WEBHOOK_SECRET:
        return jsonify({'error': 'Webhook not configured'}), 500

    if not verify_secret(request):
        return jsonify({'error': 'Invalid secret'}), 403

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
            return jsonify({
                'status': 'error',
                'message': 'Git pull failed',
                'stderr': result.stderr
            }), 500

        # Restart the application (via Docker)
        restart_result = subprocess.run(
            ['docker', 'compose', 'restart'],
            cwd=PROJECT_PATH,
            capture_output=True,
            text=True,
            timeout=120
        )

        return jsonify({
            'status': 'success',
            'git_output': result.stdout,
            'restart_output': restart_result.stdout
        })

    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Command timeout'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500
