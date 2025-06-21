#!/usr/bin/env python3
"""
クライアントの直接テスト
"""
import os
import subprocess
import time
from core.client import ExistingServerClient

def test_client_streaming():
    """クライアントのストリーミング処理をテスト"""
    
    # カスタムモックサーバーを起動
    print("📡 Starting custom mock server...")
    mock_process = subprocess.Popen([
        'python3', 'test_custom_mock_server.py'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    try:
        time.sleep(2)
        
        # 環境変数を設定
        os.environ['RESPONSE_CONTENT_FIELD'] = 'response.text'
        os.environ['RESPONSE_FINISH_FIELD'] = 'response.status'
        
        # クライアントを作成
        client = ExistingServerClient("http://localhost:3001/chat")
        
        # ストリーミングリクエストを作成
        request_data = {
            "messages": [{"role": "user", "content": "Hello"}],
            "stream": True
        }
        
        print("🌊 Testing streaming with client...")
        print("📦 Received chunks:")
        
        chunk_count = 0
        for chunk in client.send_streaming_request_dict(request_data):
            chunk_count += 1
            print(f"  Chunk {chunk_count}: {chunk}")
            
            # 無限ループを防ぐため、10チャンクで停止
            if chunk_count >= 10:
                break
                
        print(f"✅ Total chunks received: {chunk_count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("🔚 Stopping mock server...")
        mock_process.terminate()
        mock_process.wait()

if __name__ == "__main__":
    test_client_streaming()