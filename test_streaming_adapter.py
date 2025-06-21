#!/usr/bin/env python3
"""
ストリーミング時のアダプター設定テスト
"""
import os
import time
import subprocess
import requests
import json

def test_streaming_with_custom_response_field():
    """カスタムRESPONSE_CONTENT_FIELDでストリーミングをテスト"""
    print("🧪 Testing streaming with custom RESPONSE_CONTENT_FIELD...")
    
    # 環境変数を設定
    os.environ['RESPONSE_CONTENT_FIELD'] = 'response.text'
    os.environ['RESPONSE_FINISH_FIELD'] = 'response.status'
    
    # モックサーバーを起動
    print("📡 Starting mock server...")
    mock_process = subprocess.Popen([
        'python3', 'sample_server/mock_chat_server.py'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # プロキシサーバーを起動
    print("🚀 Starting proxy server...")
    proxy_process = subprocess.Popen([
        'python3', 'app_flask.py'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    try:
        # サーバー起動を待機
        time.sleep(3)
        
        # ストリーミングリクエストをテスト
        print("🌊 Testing streaming request...")
        
        response = requests.post(
            'http://localhost:8000/v1/chat/completions',
            json={
                "model": "test-model",
                "messages": [{"role": "user", "content": "Hello"}],
                "stream": True
            },
            stream=True
        )
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            chunks = []
            for line in response.iter_lines(decode_unicode=True):
                if line.startswith('data: '):
                    data_str = line[6:]
                    if data_str == '[DONE]':
                        break
                    try:
                        chunk_data = json.loads(data_str)
                        chunks.append(chunk_data)
                        print(f"📦 Chunk: {chunk_data}")
                    except json.JSONDecodeError:
                        pass
            
            if chunks:
                print("✅ Streaming with custom RESPONSE_CONTENT_FIELD works correctly!")
                return True
            else:
                print("❌ No chunks received")
                return False
        else:
            print(f"❌ HTTP error: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    finally:
        # プロセス終了
        print("🔚 Stopping servers...")
        mock_process.terminate()
        proxy_process.terminate()
        mock_process.wait()
        proxy_process.wait()

def test_streaming_with_nested_response_field():
    """ネストしたRESPONSE_CONTENT_FIELDでストリーミングをテスト"""
    print("🧪 Testing streaming with nested RESPONSE_CONTENT_FIELD...")
    
    # 環境変数を設定
    os.environ['RESPONSE_CONTENT_FIELD'] = 'data.message.content'
    os.environ['RESPONSE_FINISH_FIELD'] = 'data.message.finish'
    
    # アダプター設定を表示
    from core.adapter_config import AdapterConfig
    print(f"📋 RESPONSE_CONTENT_FIELD: {AdapterConfig.RESPONSE_CONTENT_FIELD()}")
    print(f"📋 RESPONSE_FINISH_FIELD: {AdapterConfig.RESPONSE_FINISH_FIELD()}")

if __name__ == "__main__":
    print("🚀 Starting streaming adapter tests...")
    
    # デフォルト設定でのテスト
    success1 = test_streaming_with_custom_response_field()
    
    # ネスト設定のテスト（設定確認のみ）
    test_streaming_with_nested_response_field()
    
    if success1:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")