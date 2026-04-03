import os
import json

import requests
from flask import Flask, request, jsonify, render_template_string
from jinja2 import Environment, BaseLoader
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

app = Flask(__name__)

ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY", Fernet.generate_key().decode())
cipher = Fernet(ENCRYPTION_KEY.encode() if isinstance(ENCRYPTION_KEY, str) else ENCRYPTION_KEY)

jinja_env = Environment(loader=BaseLoader())


def derive_key(password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


@app.route("/api/encrypt", methods=["POST"])
def encrypt_payload():
    data = request.get_json()
    plaintext = json.dumps(data.get("payload", {}))
    encrypted = cipher.encrypt(plaintext.encode())
    return jsonify({"encrypted": encrypted.decode()})


@app.route("/api/decrypt", methods=["POST"])
def decrypt_payload():
    data = request.get_json()
    decrypted = cipher.decrypt(data["token"].encode())
    return jsonify({"payload": json.loads(decrypted.decode())})


@app.route("/api/render", methods=["POST"])
def render_notification():
    data = request.get_json()
    template_str = data.get("template", "Hello {{ name }}")
    context = data.get("context", {})
    template = jinja_env.from_string(template_str)
    rendered = template.render(**context)
    return jsonify({"rendered": rendered})


@app.route("/api/webhook", methods=["POST"])
def forward_webhook():
    data = request.get_json()
    target_url = data.get("url")
    payload = data.get("payload", {})

    resp = requests.post(target_url, json=payload, timeout=10)
    return jsonify({"status": resp.status_code, "body": resp.text})


@app.route("/api/fetch-config")
def fetch_remote_config():
    config_url = request.args.get("source")
    resp = requests.get(config_url, timeout=5)
    return jsonify(resp.json())


@app.route("/reports/<template_name>")
def render_report(template_name):
    user_title = request.args.get("title", "Report")
    report_template = f"<h1>{user_title}</h1><p>Generated report for {{{{ org_name }}}}</p>"
    return render_template_string(report_template, org_name="Acme Corp")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
