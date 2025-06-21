#!/usr/bin/env python3
"""
動作確認用の模擬チャットサーバー

既存のチャットサーバーの動作をシミュレートし、
OpenAI Chat APIプロキシサーバーのテストに使用する
"""
import json
import time
import random
from flask import Flask, request, Response, jsonify

app = Flask(__name__)

# サンプルレスポンス
SAMPLE_RESPONSES = [
    "こんにちは！何かお手伝いできることはありますか？",
    "はい、お答えします。",
    "面白い質問ですね！詳しく説明させていただきます。",
    "それについて考えてみましょう。",
    "了解しました。以下のようになります。",
    "Hello! How can I help you today?",
    "That's an interesting question. Let me think about it.",
    "I'd be happy to help you with that.",
    "Here's what I think about this topic:",
    "Great question! Here's my response:",
]

def generate_response_content(user_message: str) -> str:
    """ユーザーメッセージに基づいてレスポンスを生成"""
    # 簡単な応答ロジック
    message_lower = user_message.lower()
    
    if "hello" in message_lower or "こんにちは" in message_lower:
        return "こんにちは！お元気ですか？何かお手伝いできることがあれば教えてください。"
    elif "thank" in message_lower or "ありがとう" in message_lower:
        return "どういたしまして！他にも何かご質問があれば遠慮なくお聞きください。"
    elif "weather" in message_lower or "天気" in message_lower:
        return "申し訳ありませんが、リアルタイムの天気情報は提供できません。お近くの天気予報サービスをご確認ください。"
    elif "python" in message_lower:
        return "Pythonは素晴らしいプログラミング言語ですね！シンプルで読みやすく、多くの分野で活用されています。"
    elif "test" in message_lower or "テスト" in message_lower:
        return "これはテスト用の模擬サーバーからの応答です。プロキシサーバーが正常に動作しています！"
    else:
        # ランダムなサンプルレスポンス
        base_response = random.choice(SAMPLE_RESPONSES)
        return f"{base_response}\n\nあなたのメッセージ「{user_message}」についてお答えします。"

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    """チャットエンドポイント"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid request"}), 400
        
        model = data.get('model', 'mock-model')
        messages = data.get('messages', [])
        stream = data.get('stream', False)
        temperature = data.get('temperature', 1.0)
        
        if not messages:
            return jsonify({"error": "No messages provided"}), 400
        
        # 最後のユーザーメッセージを取得
        user_message = ""
        for msg in reversed(messages):
            if msg.get('role') == 'user':
                user_message = msg.get('content', '')
                break
        
        # レスポンス生成
        response_content = generate_response_content(user_message)
        
        if stream:
            return handle_streaming_response(response_content, model)
        else:
            return handle_non_streaming_response(response_content, model)
            
    except Exception as e:
        app.logger.error(f"Error in chat endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

def handle_non_streaming_response(content: str, model: str):
    """非ストリーミングレスポンスを処理"""
    # 模擬的な処理時間
    time.sleep(random.uniform(0.5, 1.5))
    
    response = {
        "completionChat": content,
        "finish_reason": "stop",
        "model": model,
        "created": int(time.time())
    }
    
    return jsonify(response)

def handle_streaming_response(content: str, model: str):
    """ストリーミングレスポンスを処理"""
    def generate_stream():
        # 文字列を単語単位で分割
        words = content.split()
        
        # 開始チャンク
        yield f"data: {json.dumps({'completionChat': '', 'finish_reason': None, 'model': model})}\n\n"
        
        # 単語ごとにストリーミング
        current_content = ""
        for i, word in enumerate(words):
            # 単語間に短い遅延
            time.sleep(random.uniform(0.1, 0.3))
            
            current_content += word + " "
            chunk_data = {
                "completionChat": word + " ",
                "finish_reason": None,
                "model": model
            }
            yield f"data: {json.dumps(chunk_data, ensure_ascii=False)}\n\n"
        
        # 終了チャンク
        final_chunk = {
            "completionChat": "",
            "finish_reason": "stop",
            "model": model
        }
        yield f"data: {json.dumps(final_chunk)}\n\n"
        yield "data: [DONE]\n\n"
    
    return Response(
        generate_stream(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type'
        }
    )

@app.route('/health', methods=['GET'])
def health_check():
    """ヘルスチェックエンドポイント"""
    return jsonify({
        "status": "healthy",
        "service": "Mock Chat Server",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/chat",
            "health": "/health"
        }
    })

@app.route('/', methods=['GET'])
def root():
    """ルートエンドポイント"""
    return jsonify({
        "service": "Mock Chat Server",
        "description": "OpenAI Chat API プロキシサーバーのテスト用模擬サーバー",
        "endpoints": {
            "chat": "POST /chat",
            "health": "GET /health"
        },
        "usage": {
            "chat_request": {
                "method": "POST",
                "url": "/chat",
                "headers": {"Content-Type": "application/json"},
                "body": {
                    "model": "mock-model",
                    "messages": [
                        {"role": "user", "content": "Hello!"}
                    ],
                    "stream": False,
                    "temperature": 1.0
                }
            }
        }
    })

if __name__ == '__main__':
    print("🚀 Starting Mock Chat Server...")
    print("📍 Server will be available at: http://localhost:3333")
    print("🔗 Chat endpoint: http://localhost:3333/chat")
    print("💓 Health check: http://localhost:3333/health")
    print("📚 API info: http://localhost:3333/")
    print("\n💡 This server simulates an existing chat server for testing the OpenAI Chat API proxy.")
    print("🛑 Press Ctrl+C to stop the server\n")
    
    app.run(
        host='localhost',
        port=3333,
        debug=False,
        threaded=True
    )