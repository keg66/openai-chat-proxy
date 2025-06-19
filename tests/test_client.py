"""
既存サーバークライアントのテスト
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
import requests
from requests.exceptions import ConnectionError, Timeout, RequestException

from core.client import ExistingServerClient
from core.models import ExistingServerRequest


class TestExistingServerClient:
    """ExistingServerClientのテスト"""
    
    def setup_method(self):
        """テストの前処理"""
        self.client = ExistingServerClient(
            server_url="http://test-server.com/chat",
            timeout=30
        )
    
    def test_init(self):
        """初期化のテスト"""
        assert self.client.server_url == "http://test-server.com/chat"
        assert self.client.timeout == 30
    
    @patch('core.client.requests.post')
    def test_send_request_success(self, mock_post):
        """正常なリクエスト送信のテスト"""
        # モックレスポンスの設定
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "content": "Hello, world!",
            "finish_reason": "stop"
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # テストリクエスト作成
        request = ExistingServerRequest(
            model="test-model",
            messages=[{"role": "user", "content": "Hello"}],
            stream=False
        )
        
        # リクエスト送信
        response = self.client.send_request(request)
        
        # 結果検証
        assert response.content == "Hello, world!"
        assert response.finish_reason == "stop"
        
        # モックの呼び出し確認
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "http://test-server.com/chat"
        assert call_args[1]["json"] == request.to_dict()
        assert call_args[1]["timeout"] == 30
    
    @patch('core.client.requests.post')
    def test_send_request_connection_error(self, mock_post):
        """接続エラーのテスト"""
        mock_post.side_effect = ConnectionError("Connection failed")
        
        request = ExistingServerRequest(
            model="test-model",
            messages=[{"role": "user", "content": "Hello"}],
            stream=False
        )
        
        with pytest.raises(ConnectionError):
            self.client.send_request(request)
    
    @patch('core.client.requests.post')
    def test_send_request_timeout(self, mock_post):
        """タイムアウトエラーのテスト"""
        mock_post.side_effect = Timeout("Request timed out")
        
        request = ExistingServerRequest(
            model="test-model",
            messages=[{"role": "user", "content": "Hello"}],
            stream=False
        )
        
        with pytest.raises(Timeout):
            self.client.send_request(request)
    
    @patch('core.client.requests.post')
    def test_send_request_http_error(self, mock_post):
        """HTTPエラーのテスト"""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_post.return_value = mock_response
        
        request = ExistingServerRequest(
            model="test-model",
            messages=[{"role": "user", "content": "Hello"}],
            stream=False
        )
        
        with pytest.raises(RequestException):
            self.client.send_request(request)
    
    @patch('core.client.requests.post')
    def test_send_request_invalid_json(self, mock_post):
        """無効なJSONレスポンスのテスト"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_post.return_value = mock_response
        
        request = ExistingServerRequest(
            model="test-model",
            messages=[{"role": "user", "content": "Hello"}],
            stream=False
        )
        
        with pytest.raises(RequestException):
            self.client.send_request(request)
    
    @patch('core.client.requests.post')
    def test_send_streaming_request_success(self, mock_post):
        """ストリーミングリクエスト成功のテスト"""
        # モックレスポンスのストリーミングデータ
        streaming_data = [
            "data: {\"content\":\"Hello\",\"finish_reason\":null}\n",
            "data: {\"content\":\" world\",\"finish_reason\":null}\n",
            "data: {\"content\":\"!\",\"finish_reason\":\"stop\"}\n",
            "data: [DONE]\n"
        ]
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.iter_lines.return_value = streaming_data
        mock_post.return_value = mock_response
        
        request = ExistingServerRequest(
            model="test-model",
            messages=[{"role": "user", "content": "Hello"}],
            stream=True
        )
        
        # ストリーミングデータを収集
        chunks = list(self.client.send_streaming_request(request))
        
        # 結果検証
        assert len(chunks) == 3  # [DONE]は除外される
        assert chunks[0]["content"] == "Hello"
        assert chunks[1]["content"] == " world"
        assert chunks[2]["content"] == "!"
        assert chunks[2]["finish_reason"] == "stop"
        
        # モックの呼び出し確認
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[1]["stream"] is True
    
    @patch('core.client.requests.post')
    def test_send_streaming_request_connection_error(self, mock_post):
        """ストリーミング接続エラーのテスト"""
        mock_post.side_effect = ConnectionError("Connection failed")
        
        request = ExistingServerRequest(
            model="test-model",
            messages=[{"role": "user", "content": "Hello"}],
            stream=True
        )
        
        with pytest.raises(ConnectionError):
            list(self.client.send_streaming_request(request))
    
    @patch('core.client.requests.post')
    def test_health_check_success(self, mock_post):
        """ヘルスチェック成功のテスト"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = self.client.health_check()
        assert result is True
        
        # 短いタイムアウトで呼び出されることを確認
        call_args = mock_post.call_args
        assert call_args[1]["timeout"] == 5
    
    @patch('core.client.requests.post')
    def test_health_check_failure(self, mock_post):
        """ヘルスチェック失敗のテスト"""
        mock_post.side_effect = ConnectionError("Connection failed")
        
        result = self.client.health_check()
        assert result is False
    
    @patch('core.client.requests.post')
    def test_get_server_info(self, mock_post):
        """サーバー情報取得のテスト"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        info = self.client.get_server_info()
        
        assert info["server_url"] == "http://test-server.com/chat"
        assert info["timeout"] == 30
        assert info["health"] is True