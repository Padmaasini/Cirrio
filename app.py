import os, requests
from flask import Flask, request, jsonify

app = Flask(__name__)

GEMINI_KEY = os.environ.get('GEMINI_API_KEY', '')

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        return _cors(jsonify({}))

    if not GEMINI_KEY:
        return _cors(jsonify({'error': 'No Gemini API key configured on server'})), 500

    body = request.get_json()

    # Extract the prompt from the incoming messages array
    # Frontend sends: { messages: [{role, content}, ...], ... }
    messages = body.get('messages', [])
    system_prompt = next((m['content'] for m in messages if m['role'] == 'system'), '')
    user_prompt   = next((m['content'] for m in messages if m['role'] == 'user'), '')
    combined_prompt = f"{system_prompt}\n\n{user_prompt}" if system_prompt else user_prompt

    # Gemini 2.0 Flash with Google Search grounding (replaces Tavily RAG)
    gemini_body = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": combined_prompt}]
            }
        ],
        "tools": [
            {"google_search": {}}   # enables live Google Search grounding
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 8192,
            "responseMimeType": "text/plain"
        }
    }

    resp = requests.post(
        f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}',
        headers={'Content-Type': 'application/json'},
        json=gemini_body,
        timeout=60
    )

    if resp.status_code != 200:
        print(f"Gemini error {resp.status_code}: {resp.text}", flush=True)
        return _cors(jsonify({'error': resp.json()})), resp.status_code

    gemini_data = resp.json()

    # Extract text from Gemini response and reformat to match
    # the OpenAI-style format the frontend expects:
    # { choices: [{ message: { content: "..." } }] }
    try:
        text = gemini_data['candidates'][0]['content']['parts'][0]['text']
    except (KeyError, IndexError) as e:
        print(f"Gemini parse error: {e} — raw: {gemini_data}", flush=True)
        return _cors(jsonify({'error': 'Unexpected Gemini response format'})), 500

    # Return in OpenAI-compatible format so the frontend needs no changes
    return _cors(jsonify({
        'choices': [
            {'message': {'content': text}}
        ]
    })), 200


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
