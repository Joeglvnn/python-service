import os
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def hello():
    return jsonify({"message": "Hello from ArgoCD GitOps!"})

@app.route('/health')
def health():
    return jsonify({"status": "UP"})

if __name__ == '__main__':
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    app.run(host=host, port=8083)
