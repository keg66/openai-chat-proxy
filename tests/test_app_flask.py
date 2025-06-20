"""
Flask アプリケーションのテスト
"""
import pytest
import json
from unittest.mock import patch, Mock, MagicMock
import sys
import os

# パスの設定
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app_flask import app
from core.models import ExistingServerResponse


class TestFlaskApp:
    """Flask アプリケーションのテスト"""
    
    def setup_method(self):
        """テストの前処理"""
        app.config['TESTING'] = True
        self.client = app.test_client()
    
    def test_health_check_success(self):
        """ヘルスチェック成功のテスト"""
        with patch('app_flask.existing_client.health_check', return_value=True):
            response = self.client.get('/health')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'healthy'
            assert data['existing_server']['healthy'] is True
    
    def test_health_check_degraded(self):
        """ヘルスチェック劣化のテスト"""
        with patch('app_flask.existing_client.health_check', return_value=False):
            response = self.client.get('/health')
            
            assert response.status_code == 503
            data = json.loads(response.data)
            assert data['status'] == 'degraded'
            assert data['existing_server']['healthy'] is False
    
    def test_health_check_error(self):
        """ヘルスチェックエラーのテスト"""
        with patch('app_flask.existing_client.health_check', side_effect=Exception("Test error")):
            response = self.client.get('/health')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert data['status'] == 'unhealthy'
            assert 'error' in data
    
    def test_chat_completions_invalid_content_type(self):
        """無効なContent-Typeのテスト"""
        response = self.client.post('/v1/chat/completions', data='not json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error']['message'] == 'Request must be JSON'
    
    def test_chat_completions_empty_body(self):
        """空のリクエストボディのテスト"""
        response = self.client.post('/v1/chat/completions', 
                                  data='',
                                  content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error']['message'] == 'Invalid JSON'
    
    def test_chat_completions_missing_model(self):
        """モデルパラメータ不足のテスト"""
        request_data = {
            "messages": [{"role": "user", "content": "Hello"}]
        }
        
        response = self.client.post('/v1/chat/completions', json=request_data)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Missing required parameter: model' in data['error']['message']
    
    def test_chat_completions_missing_messages(self):
        """メッセージパラメータ不足のテスト"""
        request_data = {
            "model": "gpt-3.5-turbo"
        }
        
        response = self.client.post('/v1/chat/completions', json=request_data)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Missing required parameter: messages' in data['error']['message']
    
    def test_chat_completions_empty_messages(self):
        """空のメッセージ配列のテスト"""
        request_data = {
            "model": "gpt-3.5-turbo",
            "messages": []
        }
        
        response = self.client.post('/v1/chat/completions', json=request_data)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Messages must be a non-empty array' in data['error']['message']
    
    def test_chat_completions_invalid_messages_format(self):
        """無効なメッセージ形式のテスト"""
        request_data = {
            "model": "gpt-3.5-turbo",
            "messages": "not an array"
        }
        
        response = self.client.post('/v1/chat/completions', json=request_data)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Messages must be a non-empty array' in data['error']['message']
    
    @patch('app_flask.existing_client.send_request_dict')
    def test_chat_completions_non_streaming_success(self, mock_send_request_dict):
        """非ストリーミング成功のテスト"""
        # モックレスポンスの設定（新しい形式では辞書）
        mock_response = {
            "content": "Hello! How can I help you today?",
            "finish_reason": "stop"
        }
        mock_send_request_dict.return_value = mock_response
        
        request_data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "Hello"}],
            "temperature": 0.7,
            "max_tokens": 100
        }
        
        response = self.client.post('/v1/chat/completions', json=request_data)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['object'] == 'chat.completion'
        assert data['model'] == 'gpt-3.5-turbo'
        assert len(data['choices']) == 1
        assert data['choices'][0]['message']['role'] == 'assistant'
        assert data['choices'][0]['message']['content'] == 'Hello! How can I help you today?'
        assert data['choices'][0]['finish_reason'] == 'stop'
        assert 'usage' in data
        assert data['usage']['total_tokens'] > 0
    
    @patch('app_flask.existing_client.send_request_dict')
    def test_chat_completions_connection_error(self, mock_send_request_dict):
        """接続エラーのテスト"""
        from requests.exceptions import ConnectionError
        mock_send_request_dict.side_effect = ConnectionError("Connection failed")
        
        request_data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "Hello"}]
        }
        
        response = self.client.post('/v1/chat/completions', json=request_data)
        
        assert response.status_code == 503
        data = json.loads(response.data)
        assert data['error']['type'] == 'service_unavailable'
    
    @patch('app_flask.existing_client.send_request_dict')
    def test_chat_completions_timeout_error(self, mock_send_request_dict):
        """タイムアウトエラーのテスト"""
        from requests.exceptions import Timeout
        mock_send_request_dict.side_effect = Timeout("Request timed out")
        
        request_data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "Hello"}]
        }
        
        response = self.client.post('/v1/chat/completions', json=request_data)
        
        assert response.status_code == 504
        data = json.loads(response.data)
        assert data['error']['type'] == 'timeout'
    
    @patch('app_flask.existing_client.send_streaming_request_dict')
    def test_chat_completions_streaming_success(self, mock_send_streaming_request_dict):
        """ストリーミング成功のテスト"""
        # モックストリーミングデータ
        streaming_data = [
            {"content": "Hello", "finish_reason": None},
            {"content": " there", "finish_reason": None},
            {"content": "!", "finish_reason": "stop"}
        ]
        mock_send_streaming_request_dict.return_value = iter(streaming_data)
        
        request_data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "Hello"}],
            "stream": True
        }
        
        response = self.client.post('/v1/chat/completions', json=request_data)
        
        assert response.status_code == 200
        assert response.content_type == 'text/event-stream; charset=utf-8'
        
        # ストリーミングデータの検証
        response_text = response.data.decode('utf-8')
        assert 'data: ' in response_text
        assert 'data: [DONE]' in response_text
    
    def test_not_found_error(self):
        """404エラーのテスト"""
        response = self.client.get('/nonexistent')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['error']['type'] == 'not_found_error'
    
    @patch('app_flask.existing_client.send_request_dict')
    def test_invalid_request_format(self, mock_send_request_dict):
        """無効なリクエスト形式のテスト"""
        # モックレスポンスの設定（新しい形式では辞書）
        mock_response = {
            "content": "Hello! This is a valid response.",
            "finish_reason": "stop"
        }
        mock_send_request_dict.return_value = mock_response
        
        request_data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "invalid_role", "content": "Hello"}]
        }
        
        response = self.client.post('/v1/chat/completions', json=request_data)
        
        # 無効なroleでも現在の実装では処理される（既存サーバーが受け付ける場合）
        assert response.status_code == 200