#!/bin/bash

# モックサーバー クイックテスト

echo "⚡ Quick Mock Server Test"
echo "========================"

MOCK_SERVER_URL="http://localhost:3000"

# サーバーチェック
if ! curl -s "$MOCK_SERVER_URL/health" > /dev/null; then
    echo "❌ Mock server not running on port 3000"
    echo "   Start with: python sample_server/mock_chat_server.py"
    exit 1
fi

echo "✅ Mock server is running"
echo ""

# シンプルなチャットテスト
echo "💬 Testing chat functionality..."
echo ""

response=$(curl -s -X POST "$MOCK_SERVER_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "test-model",
    "messages": [
      {"role": "user", "content": "Hello! Please respond with a short greeting."}
    ],
    "stream": false
  }')

if [ $? -eq 0 ]; then
    echo "📨 Request sent successfully"
    echo "🤖 Response:"
    echo "$response" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(f\"   Content: {data.get('content', 'No content')}\")
    print(f\"   Model: {data.get('model', 'No model')}\")
    print(f\"   Status: {data.get('finish_reason', 'No status')}\")
except:
    print('   Error parsing response')
"
    echo ""
    echo "✅ Mock server is working correctly!"
else
    echo "❌ Request failed"
    exit 1
fi

echo ""
echo "🎯 Ready for proxy server testing!"