#!/usr/bin/env python3
"""
カスタムフィールドを使用するテスト用モックサーバー
"""
from flask import Flask, request, Response, jsonify
import json
import time

app = Flask(__name__)

@app.route('/chat', methods=['POST'])
def chat():
    """カスタムフィールドでレスポンスするチャットエンドポイント"""
    try:
        data = request.get_json()
        stream = data.get('stream', False)
        
        if stream:
            def generate_streaming_response():
                # カスタムフィールド構造でストリーミングレスポンス
                chunks = [
                    {"response": {"text": "", "status": None}, "model": "custom-model"},
                    {"response": {"text": "Hello from custom fields ", "status": None}, "model": "custom-model"},
                    {"response": {"text": "This is using response.text field.", "status": None}, "model": "custom-model"},
                    {"response": {"text": "", "status": "stop"}, "model": "custom-model"}
                ]
                
                for chunk in chunks:
                    yield f"data: {json.dumps(chunk)}\n\n"
                    time.sleep(0.1)
                
                yield "data: [DONE]\n\n"
            
            return Response(
                generate_streaming_response(),
                content_type='text/event-stream'
            )
        else:
            # 非ストリーミングレスポンス
            return jsonify({
                "response": {
                    "text": "Hello from custom fields",
                    "status": "stop"
                },
                "model": "custom-model"
            })
            
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    print("🚀 Starting Custom Mock Server...")
    print("📍 Server will be available at: http://localhost:3001")
    print("🔗 Chat endpoint: http://localhost:3001/chat")
    print("💡 This server uses custom response fields (response.text, response.status)")
    app.run(host='localhost', port=3001, debug=False)