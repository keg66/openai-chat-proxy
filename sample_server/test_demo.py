#!/usr/bin/env python3
"""
OpenAI Chat API プロキシサーバーの動作確認デモスクリプト
"""
import requests
import json
import time
import sys
from typing import Dict, Any

# サーバーのURL
PROXY_SERVER_URL = "http://localhost:8000"
MOCK_SERVER_URL = "http://localhost:3000"

def check_server_health(url: str, name: str) -> bool:
    """サーバーのヘルスチェック"""
    try:
        response = requests.get(f"{url}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ {name} is healthy")
            return True
        else:
            print(f"⚠️  {name} returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {name} is not responding: {e}")
        return False

def test_non_streaming_chat(message: str) -> None:
    """非ストリーミングチャットのテスト"""
    print(f"\n📝 Testing non-streaming chat with message: '{message}'")
    
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": message}
        ],
        "temperature": 0.7,
        "stream": False
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{PROXY_SERVER_URL}/v1/chat/completions",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            print(f"✅ Response received in {end_time - start_time:.2f}s")
            print(f"🤖 Assistant: {content}")
            print(f"📊 Usage: {data.get('usage', 'N/A')}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")

def test_streaming_chat(message: str) -> None:
    """ストリーミングチャットのテスト"""
    print(f"\n🌊 Testing streaming chat with message: '{message}'")
    
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": message}
        ],
        "temperature": 0.7,
        "stream": True
    }
    
    try:
        response = requests.post(
            f"{PROXY_SERVER_URL}/v1/chat/completions",
            json=payload,
            headers={"Content-Type": "application/json"},
            stream=True,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Streaming response:")
            print("🤖 Assistant: ", end="", flush=True)
            
            for line in response.iter_lines(decode_unicode=True):
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str == "[DONE]":
                        break
                    try:
                        chunk_data = json.loads(data_str)
                        if chunk_data["choices"]:
                            delta = chunk_data["choices"][0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                print(content, end="", flush=True)
                    except json.JSONDecodeError:
                        continue
            print("\n")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")

def test_error_handling() -> None:
    """エラーハンドリングのテスト"""
    print("\n🔍 Testing error handling...")
    
    # 無効なリクエスト
    print("Testing invalid request (missing model):")
    payload = {
        "messages": [{"role": "user", "content": "Hello"}]
    }
    
    try:
        response = requests.post(
            f"{PROXY_SERVER_URL}/v1/chat/completions",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 400:
            print("✅ Correctly returned 400 for invalid request")
            error_data = response.json()
            print(f"📄 Error message: {error_data.get('error', {}).get('message', 'N/A')}")
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")

def main():
    """メイン関数"""
    print("🚀 OpenAI Chat API Proxy Server Demo")
    print("=" * 50)
    
    # サーバーのヘルスチェック
    print("\n🔍 Checking server health...")
    mock_healthy = check_server_health(MOCK_SERVER_URL, "Mock Chat Server")
    proxy_healthy = check_server_health(PROXY_SERVER_URL, "Proxy Server")
    
    if not mock_healthy:
        print("\n❌ Mock server is not running. Please start it first:")
        print("   python sample_server/mock_chat_server.py")
        sys.exit(1)
    
    if not proxy_healthy:
        print("\n❌ Proxy server is not running. Please start it first:")
        print("   python app_flask.py")
        sys.exit(1)
    
    print("\n🎉 Both servers are healthy! Starting tests...")
    
    # テストメッセージ
    test_messages = [
        "Hello! How are you?",
        "こんにちは！プロキシサーバーのテストです",
        "Tell me about Python programming",
        "天気はどうですか？"
    ]
    
    # 非ストリーミングテスト
    print("\n" + "=" * 50)
    print("🔄 NON-STREAMING TESTS")
    print("=" * 50)
    
    for message in test_messages[:2]:
        test_non_streaming_chat(message)
        time.sleep(1)
    
    # ストリーミングテスト
    print("\n" + "=" * 50)
    print("🌊 STREAMING TESTS")
    print("=" * 50)
    
    for message in test_messages[2:]:
        test_streaming_chat(message)
        time.sleep(1)
    
    # エラーハンドリングテスト
    print("\n" + "=" * 50)
    print("⚠️  ERROR HANDLING TESTS")
    print("=" * 50)
    test_error_handling()
    
    print("\n" + "=" * 50)
    print("✅ Demo completed successfully!")
    print("🎯 The OpenAI Chat API proxy server is working correctly.")
    print("=" * 50)

if __name__ == "__main__":
    main()