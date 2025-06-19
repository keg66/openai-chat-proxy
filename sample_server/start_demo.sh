#!/bin/bash

# OpenAI Chat API プロキシサーバーのデモ起動スクリプト

echo "🚀 Starting OpenAI Chat API Proxy Demo"
echo "======================================"

# 仮想環境の確認
if [ ! -d "../venv" ]; then
    echo "❌ Virtual environment not found. Please run:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# カレントディレクトリを確認
if [ ! -f "mock_chat_server.py" ]; then
    echo "❌ Please run this script from the sample_server directory"
    echo "   cd sample_server"
    echo "   ./start_demo.sh"
    exit 1
fi

echo "📝 Step 1: Starting Mock Chat Server (port 3000)..."
cd ..
source venv/bin/activate

# モックサーバーをバックグラウンドで起動
python sample_server/mock_chat_server.py &
MOCK_PID=$!
echo "✅ Mock server started with PID: $MOCK_PID"

# モックサーバーの起動を待つ
echo "⏳ Waiting for mock server to start..."
sleep 3

echo ""
echo "📝 Step 2: Starting Proxy Server (port 8000)..."
# プロキシサーバーをバックグラウンドで起動
python app_flask.py &
PROXY_PID=$!
echo "✅ Proxy server started with PID: $PROXY_PID"

# プロキシサーバーの起動を待つ
echo "⏳ Waiting for proxy server to start..."
sleep 3

echo ""
echo "📝 Step 3: Running demo tests..."
echo "🔍 Testing the proxy server functionality..."
python sample_server/test_demo.py

echo ""
echo "🛑 Stopping servers..."
kill $MOCK_PID 2>/dev/null
kill $PROXY_PID 2>/dev/null

echo "✅ Demo completed!"
echo ""
echo "📚 Manual testing URLs:"
echo "   Mock Server:  http://localhost:3000"
echo "   Proxy Server: http://localhost:8000"
echo "   Health Check: http://localhost:8000/health"