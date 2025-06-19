#!/bin/bash

# cURLを使った動作確認例

echo "🌐 OpenAI Chat API Proxy - cURL Examples"
echo "========================================"

# ヘルスチェック
echo ""
echo "📍 1. Health Check"
echo "curl http://localhost:8000/health"
echo "---"
curl -s http://localhost:8000/health | python3 -m json.tool
echo ""

# 非ストリーミングチャット
echo "📍 2. Non-streaming Chat"
echo "curl -X POST http://localhost:8000/v1/chat/completions ..."
echo "---"
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {"role": "user", "content": "Hello! This is a test message."}
    ],
    "temperature": 0.7
  }' | python3 -m json.tool
echo ""

# ストリーミングチャット
echo "📍 3. Streaming Chat"
echo "curl -X POST http://localhost:8000/v1/chat/completions ... (stream=true)"
echo "---"
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {"role": "user", "content": "Tell me a short story about a robot."}
    ],
    "stream": true,
    "temperature": 0.7
  }'
echo ""
echo ""

# エラーテスト
echo "📍 4. Error Test (Missing model parameter)"
echo "curl -X POST http://localhost:8000/v1/chat/completions ... (no model)"
echo "---"
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "This should fail"}
    ]
  }' | python3 -m json.tool
echo ""

echo "✅ cURL examples completed!"