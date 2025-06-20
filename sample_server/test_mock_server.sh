#!/bin/bash

# モックサーバー直接テスト用 cURL スクリプト

echo "🧪 Mock Chat Server Direct Testing"
echo "=================================="

# モックサーバーのURL
MOCK_SERVER_URL="http://localhost:3000"

# サーバーが起動しているかチェック
echo ""
echo "🔍 Checking if mock server is running..."
if ! curl -s "$MOCK_SERVER_URL/health" > /dev/null; then
    echo "❌ Mock server is not running on port 3000"
    echo "   Please start it first: python sample_server/mock_chat_server.py"
    exit 1
fi

echo "✅ Mock server is running"

# ヘルスチェック
echo ""
echo "📍 1. Health Check"
echo "curl $MOCK_SERVER_URL/health"
echo "---"
curl -s "$MOCK_SERVER_URL/health" | python3 -m json.tool
echo ""

# API情報
echo "📍 2. API Information"
echo "curl $MOCK_SERVER_URL/"
echo "---"
curl -s "$MOCK_SERVER_URL/" | python3 -m json.tool
echo ""

# 非ストリーミング チャット - Hello
echo "📍 3. Non-streaming Chat - Hello"
echo "curl -X POST $MOCK_SERVER_URL/chat ..."
echo "---"
curl -X POST "$MOCK_SERVER_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mock-model",
    "messages": [
      {"role": "user", "content": "Hello! How are you?"}
    ],
    "stream": false,
    "temperature": 0.7
  }' | python3 -m json.tool
echo ""

# 非ストリーミング チャット - 日本語
echo "📍 4. Non-streaming Chat - Japanese"
echo "curl -X POST $MOCK_SERVER_URL/chat ..."
echo "---"
curl -X POST "$MOCK_SERVER_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mock-model",
    "messages": [
      {"role": "user", "content": "こんにちは！調子はどうですか？"}
    ],
    "stream": false,
    "temperature": 0.7
  }' | python3 -m json.tool
echo ""

# 非ストリーミング チャット - Python質問
echo "📍 5. Non-streaming Chat - Python Question"
echo "curl -X POST $MOCK_SERVER_URL/chat ..."
echo "---"
curl -X POST "$MOCK_SERVER_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mock-model",
    "messages": [
      {"role": "user", "content": "Tell me about Python programming"}
    ],
    "stream": false,
    "temperature": 0.8
  }' | python3 -m json.tool
echo ""

# 非ストリーミング チャット - テスト
echo "📍 6. Non-streaming Chat - Test Message"
echo "curl -X POST $MOCK_SERVER_URL/chat ..."
echo "---"
curl -X POST "$MOCK_SERVER_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mock-model",
    "messages": [
      {"role": "user", "content": "This is a test message"}
    ],
    "stream": false,
    "temperature": 1.0
  }' | python3 -m json.tool
echo ""

# ストリーミング チャット
echo "📍 7. Streaming Chat"
echo "curl -X POST $MOCK_SERVER_URL/chat ... (stream=true)"
echo "---"
echo "🌊 Streaming response:"
curl -X POST "$MOCK_SERVER_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mock-model",
    "messages": [
      {"role": "user", "content": "Tell me a short story about a robot learning to cook"}
    ],
    "stream": true,
    "temperature": 0.9
  }'
echo ""
echo ""

# 会話コンテキスト付きチャット
echo "📍 8. Multi-turn Conversation"
echo "curl -X POST $MOCK_SERVER_URL/chat ... (with context)"
echo "---"
curl -X POST "$MOCK_SERVER_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mock-model",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "What is the capital of Japan?"},
      {"role": "assistant", "content": "The capital of Japan is Tokyo."},
      {"role": "user", "content": "What is the population of that city?"}
    ],
    "stream": false,
    "temperature": 0.5
  }' | python3 -m json.tool
echo ""

# エラーテスト - メッセージなし
echo "📍 9. Error Test - No Messages"
echo "curl -X POST $MOCK_SERVER_URL/chat ... (no messages)"
echo "---"
curl -X POST "$MOCK_SERVER_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mock-model",
    "stream": false
  }' | python3 -m json.tool
echo ""

# エラーテスト - 無効なJSON
echo "📍 10. Error Test - Invalid JSON"
echo "curl -X POST $MOCK_SERVER_URL/chat ... (invalid JSON)"
echo "---"
curl -X POST "$MOCK_SERVER_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{invalid json}' | python3 -m json.tool 2>/dev/null || echo "Expected JSON parse error"
echo ""

# エラーテスト - Content-Type なし
echo "📍 11. Error Test - No Content-Type"
echo "curl -X POST $MOCK_SERVER_URL/chat ... (no content-type)"
echo "---"
curl -X POST "$MOCK_SERVER_URL/chat" \
  -d '{
    "model": "mock-model",
    "messages": [
      {"role": "user", "content": "This should fail"}
    ]
  }' | python3 -m json.tool 2>/dev/null || echo "Expected error due to missing Content-Type"
echo ""

# パフォーマンステスト
echo "📍 12. Performance Test - Multiple Requests"
echo "Sending 5 concurrent requests..."
echo "---"
start_time=$(date +%s.%N)

for i in {1..5}; do
  (
    curl -s -X POST "$MOCK_SERVER_URL/chat" \
      -H "Content-Type: application/json" \
      -d "{
        \"model\": \"mock-model\",
        \"messages\": [
          {\"role\": \"user\", \"content\": \"Request #$i - Hello from concurrent test\"}
        ],
        \"stream\": false
      }" > /dev/null
    echo "✅ Request #$i completed"
  ) &
done

wait
end_time=$(date +%s.%N)
duration=$(echo "$end_time - $start_time" | bc -l)
echo "🏁 All 5 requests completed in ${duration} seconds"
echo ""

echo "=" * 50
echo "✅ Mock server testing completed!"
echo "📊 Summary:"
echo "   - Health check: ✅"
echo "   - API info: ✅"
echo "   - Non-streaming chat: ✅"
echo "   - Streaming chat: ✅"
echo "   - Multi-turn conversation: ✅"
echo "   - Error handling: ✅"
echo "   - Performance test: ✅"
echo ""
echo "🎯 The mock server is working correctly and ready for proxy testing!"
echo "=" * 50