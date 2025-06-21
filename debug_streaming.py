#!/usr/bin/env python3
"""
ストリーミング処理のデバッグスクリプト
"""
import os
import time
import subprocess
import requests
import json

def test_streaming_debug():
    """詳細なストリーミングデバッグ"""
    
    # 環境変数を設定
    os.environ['EXISTING_SERVER_URL'] = 'http://localhost:3001/chat'
    os.environ['RESPONSE_CONTENT_FIELD'] = 'response.text'
    os.environ['RESPONSE_FINISH_FIELD'] = 'response.status'
    os.environ['ADAPTER_DEBUG'] = 'true'
    os.environ['LOG_LEVEL'] = 'DEBUG'
    
    print("🔧 Debug configuration:")
    print(f"  EXISTING_SERVER_URL: {os.environ['EXISTING_SERVER_URL']}")
    print(f"  RESPONSE_CONTENT_FIELD: {os.environ['RESPONSE_CONTENT_FIELD']}")
    print(f"  RESPONSE_FINISH_FIELD: {os.environ['RESPONSE_FINISH_FIELD']}")
    print()
    
    # カスタムモックサーバーを起動
    print("📡 Starting custom mock server...")
    mock_process = subprocess.Popen([
        'python3', 'test_custom_mock_server.py'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # プロキシサーバーを起動
    print("🚀 Starting proxy server with debug...")
    proxy_process = subprocess.Popen([
        'python3', 'app_flask.py'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    try:
        # サーバー起動を待機
        time.sleep(4)
        
        # まず、カスタムモックサーバーを直接テスト
        print("🧪 Testing custom mock server directly...")
        response = requests.post(
            'http://localhost:3001/chat',
            json={
                "messages": [{"role": "user", "content": "Hello"}],
                "stream": True
            },
            stream=True
        )
        
        print("📡 Direct mock server response:")
        for line in response.iter_lines(decode_unicode=True):
            if line.strip():
                print(f"  {line}")
                if line == "data: [DONE]":
                    break
        print()
        
        # プロキシサーバー経由でテスト
        print("🌐 Testing via proxy server...")
        response = requests.post(
            'http://localhost:8000/v1/chat/completions',
            json={
                "model": "test-model",
                "messages": [{"role": "user", "content": "Hello"}],
                "stream": True
            },
            stream=True
        )
        
        print("📡 Proxy server response:")
        for line in response.iter_lines(decode_unicode=True):
            if line.strip():
                print(f"  {line}")
                if line == "data: [DONE]":
                    break
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    finally:
        # プロセス終了
        print("\n🔚 Stopping servers...")
        mock_process.terminate()
        proxy_process.terminate()
        mock_process.wait()
        proxy_process.wait()

if __name__ == "__main__":
    test_streaming_debug()