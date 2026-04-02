import os, requests
from flask import Flask, request, jsonify

app = Flask(__name__)

GROQ_KEY = os.environ.get('GROQ_API_KEY', '')

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        return _cors(jsonify({}))

    if not GROQ_KEY:
        return _cors(jsonify({'error': 'No API key configured on server'})), 500

    resp = requests.post(
        'https://api.groq.com/openai/v1/chat/completions',
        headers={
            'Content-Type':  'application/json',
            'Authorization': 'Bearer ' + GROQ_KEY
        },
        json=request.get_json()
    )

    return _cors(jsonify(resp.json())), resp.status_code

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        return _cors(jsonify({}))

    if not GROQ_KEY:
        return _cors(jsonify({'error': 'No API key configured on server'})), 500

    resp = requests.post(
        'https://api.groq.com/openai/v1/chat/completions',
        headers={
            'Content-Type':  'application/json',
            'Authorization': 'Bearer ' + GROQ_KEY
        },
        json=request.get_json()
    )

    # ← ADD THIS: log the error so it appears in Render logs
    if resp.status_code != 200:
        print(f"Groq error {resp.status_code}: {resp.text}", flush=True)

    return _cors(jsonify(resp.json())), resp.status_code
