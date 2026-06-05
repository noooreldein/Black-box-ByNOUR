import requests
import json
import uuid
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

MY_OWNER = "@n_7_3_a"
MY_CHANNEL = "https://t.me/n_7_3_a_2"
MY_NAME = "Noor"

BLACKBOX_URL = "https://app.blackbox.ai/api/chat"

HEADERS = {
    'authority': 'app.blackbox.ai',
    'accept': '*/*',
    'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
    'content-type': 'application/json',
    'origin': 'https://app.blackbox.ai',
    'referer': 'https://app.blackbox.ai/chat/tQacSfC',
    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
}

COOKIES = {
    'sessionId': '6f65cf27-8f4e-42d3-ac9a-ad0f3923e2f9',
    'userCountry': '%7B%22country%22%3A%22EG%22%2C%22currency%22%3A%22EGP%22%2C%22timestamp%22%3A1774257557213%2C%22expires%22%3A1774862357213%7D',
    '__Host-authjs.csrf-token': '7f56ff4c67126f0d90b996219ab375578649f1f3604b0b6263f7eb47a5d2a691%7C5191e436f5faf9807bf1ba88a4e13c1a623210e56228baa2ee4fe689bd8bc882',
    '__Secure-authjs.callback-url': 'https%3A%2F%2Fapp.blackbox.ai',
}

# تخزين الجلسات (للذاكرة)
sessions = {}

def build_json_data(messages):
    return {
        'messages': messages,
        'id': 'tQacSfC',
        'previewToken': None,
        'userId': None,
        'codeModelMode': True,
        'trendingAgentMode': {},
        'isMicMode': False,
        'userSystemPrompt': None,
        'maxTokens': 4000,
        'playgroundTopP': None,
        'playgroundTemperature': None,
        'isChromeExt': False,
        'githubToken': '',
        'clickedAnswer2': False,
        'clickedAnswer3': False,
        'clickedForceWebSearch': False,
        'visitFromDelta': False,
        'isMemoryEnabled': False,
        'mobileClient': False,
        'userSelectedModel': None,
        'userSelectedAgent': 'VscodeAgent',
        'validated': 'a38f5889-8fef-46d4-8ede-bf4668b6a9bb',
        'imageGenerationMode': False,
        'imageGenMode': 'autoMode',
        'webSearchModePrompt': False,
        'deepSearchMode': False,
        'promptSelection': '',
        'domains': None,
        'vscodeClient': False,
        'codeInterpreterMode': False,
        'customProfile': {
            'name': '',
            'occupation': '',
            'traits': [],
            'additionalInfo': '',
            'enableNewChats': False,
        },
        'webSearchModeOption': {
            'autoMode': True,
            'webMode': False,
            'offlineMode': False,
        },
        'session': None,
        'isPremium': False,
        'teamAccount': '',
        'subscriptionCache': None,
        'beastMode': False,
        'reasoningMode': False,
        'designerMode': False,
        'workspaceId': '',
        'asyncMode': False,
        'integrations': {},
        'isTaskPersistent': False,
        'selectedElement': None,
    }

@app.route('/')
def home():
    return jsonify({
        "status": "running",
        "api": "Blackbox API (WormGPT Style) by Noor",
        "usage": "GET /chat?q=سؤالك",
        "optional_params": "session_id (للذاكرة), raw=1 (للرد الخام)",
        "owner": MY_OWNER,
        "channel": MY_CHANNEL,
        "developer": MY_NAME
    })

@app.route('/chat', methods=['GET'])
def chat():
    try:
        # استقبال السؤال
        question = request.args.get('q', '') or request.args.get('text', '')
        if not question:
            return jsonify({"status": "error", "message": "استخدم ?q=سؤالك"}), 400

        session_id = request.args.get('session_id', str(uuid.uuid4())[:8])
        raw_mode = request.args.get('raw', '0') == '1'

        # إنشاء أو استرجاع الجلسة
        if session_id not in sessions:
            sessions[session_id] = {'messages': []}
        session = sessions[session_id]

        # إضافة رسالة المستخدم
        session['messages'].append({
            'role': 'user',
            'content': question,
            'id': str(uuid.uuid4())[:8],
        })

        # إرسال الطلب لـ Blackbox
        json_data = build_json_data(session['messages'])
        response = requests.post(
            BLACKBOX_URL,
            cookies=COOKIES,
            headers=HEADERS,
            json=json_data,
            timeout=60
        )

        if response.status_code != 200:
            return jsonify({
                "status": "error",
                "message": f"فشل الاتصال بـ Blackbox: {response.status_code}"
            }), 500

        raw_reply = response.text

        # حفظ الرد في الجلسة
        session['messages'].append({
            'role': 'assistant',
            'content': raw_reply,
            'id': str(uuid.uuid4())[:8],
        })

        # الرد النهائي (خام أو منقى)
        final_reply = raw_reply  # الخام افتراضيًا إذا raw=1، لكننا سنقدم الخيار
        if not raw_mode:
            # تنظيف سريع لإزالة وسوم think و HTML
            import re
            clean = re.sub(r'<think>.*?</think>', '', raw_reply, flags=re.DOTALL)
            clean = re.sub(r'<[^>]+>', '', clean)
            clean = re.sub(r'\s+', ' ', clean).strip()
            final_reply = clean

        return jsonify({
            "status": "success",
            "reply": final_reply,
            "session_id": session_id,
            "owner": MY_OWNER,
            "channel": MY_CHANNEL,
            "developer": MY_NAME
        })

    except requests.exceptions.Timeout:
        return jsonify({"status": "error", "message": "انتهى وقت الاتصال"}), 504
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Blackbox API (WormGPT Style) شغال على المنفذ {port}")
    app.run(host='0.0.0.0', port=port)
