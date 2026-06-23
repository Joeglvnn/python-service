from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def hello():
    return jsonify({"message": "Hello from Python Flask service!"})

@app.route('/health')
def health():
    return jsonify({"status": "UP"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8083)# Fix missing ensurepip module
