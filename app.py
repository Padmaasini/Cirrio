import os, requests
from flask import Flask, request, jsonify

app = Flask(__name__)

GROQ_KEY   = os.environ.get('GROQ_API_KEY', '')
TAVILY_KEY = os.environ.get('TAVILY_API_KEY', '')

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        return _cors(jsonify({}))
    if not GROQ_KEY:
        return _cors(jsonify({'error': 'No Groq API key configured'})), 500
    resp = requests.post(
        'https://api.groq.com/openai/v1/chat/completions',
        headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + GROQ_KEY},
        json=request.get_json(),
        timeout=60
    )
    return _cors(jsonify(resp.json())), resp.status_code

@app.route('/api/search', methods=['POST', 'OPTIONS'])
def search():
    if request.method == 'OPTIONS':
        return _cors(jsonify({}))
    if not TAVILY_KEY:
        return _cors(jsonify({'answer': '', 'results': []})), 200
    body = request.get_json()
    body['api_key'] = TAVILY_KEY
    resp = requests.post('https://api.tavily.com/search', json=body, timeout=15)
    return _cors(jsonify(resp.json())), resp.status_code

@app.route('/health')
def health():
    return jsonify({
        'status': 'ok',
        'groq':   'configured' if GROQ_KEY   else 'missing',
        'tavily': 'configured' if TAVILY_KEY else 'not set (optional)'
    }), 200

def _cors(r):
    r.headers['Access-Control-Allow-Origin']  = '*'
    r.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
    r.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return r

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))
