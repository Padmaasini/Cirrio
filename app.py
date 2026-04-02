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

@app.route('/health')
def health():
    return 'OK', 200

def _cors(response):
    response.headers['Access-Control-Allow-Origin']  = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))
