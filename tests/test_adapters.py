"""
アダプタークラスのテスト
"""
import pytest
import json
from unittest.mock import Mock, patch
from core.adapters.configurable import ConfigurableAdapter
from core.adapters.factory import AdapterFactory, get_default_adapter
from core.adapters.base import BaseAdapter, AdapterError, MappingError
from core.adapter_config import AdapterConfig
from core.models import ChatCompletionRequest, ChatMessage, ExistingServerResponse


class MockConfig:
    """テスト用のモック設定"""
    @staticmethod
    def ADAPTER_TYPE():
        return "configurable"  # 既存のタイプを使用
    
    @staticmethod
    def REQUEST_MESSAGES_FIELD():
        return "messages"
    
    @staticmethod
    def REQUEST_MODEL_FIELD():
        return "model"
    
    @staticmethod
    def REQUEST_TEMPERATURE_FIELD():
        return "temperature"
    
    @staticmethod
    def REQUEST_MAX_TOKENS_FIELD():
        return "max_tokens"
    
    @staticmethod
    def REQUEST_STREAM_FIELD():
        return "stream"
    
    @staticmethod
    def REQUEST_STOP_FIELD():
        return "stop"
    
    @staticmethod
    def RESPONSE_CONTENT_FIELD():
        return "content"
    
    @staticmethod
    def RESPONSE_FINISH_FIELD():
        return "finish_reason"
    
    @staticmethod
    def RESPONSE_MODEL_FIELD():
        return "model"
    
    @staticmethod
    def RESPONSE_CREATED_FIELD():
        return "created"
    
    @staticmethod
    def STREAMING_FORMAT():
        return "sse"
    
    @staticmethod
    def STREAMING_DATA_PREFIX():
        return "data: "
    
    @staticmethod
    def STREAMING_DONE_MARKER():
        return "[DONE]"
    
    @staticmethod
    def CUSTOM_HEADERS():
        return {}
    
    @staticmethod
    def REQUEST_TRANSFORM():
        return "none"
    
    @staticmethod
    def RESPONSE_TRANSFORM():
        return "none"
    
    @staticmethod
    def ADAPTER_DEBUG():
        return False
    
    @classmethod
    def validate(cls):
        """テスト用の検証メソッド"""
        pass


class CustomFieldConfig:
    """カスタムフィールド設定"""
    @staticmethod
    def ADAPTER_TYPE():
        return "configurable"
    
    @staticmethod
    def REQUEST_MESSAGES_FIELD():
        return "conversation"
    
    @staticmethod
    def REQUEST_MODEL_FIELD():
        return "engine"
    
    @staticmethod
    def REQUEST_TEMPERATURE_FIELD():
        return "randomness"
    
    @staticmethod
    def REQUEST_MAX_TOKENS_FIELD():
        return ""  # 無効化
    
    @staticmethod
    def REQUEST_STREAM_FIELD():
        return "streaming_mode"
    
    @staticmethod
    def REQUEST_STOP_FIELD():
        return ""
    
    @staticmethod
    def RESPONSE_CONTENT_FIELD():
        return "response.text"
    
    @staticmethod
    def RESPONSE_FINISH_FIELD():
        return "response.status"
    
    @staticmethod
    def RESPONSE_MODEL_FIELD():
        return ""  # 無効化
    
    @staticmethod
    def RESPONSE_CREATED_FIELD():
        return ""
    
    @staticmethod
    def STREAMING_FORMAT():
        return "jsonlines"
    
    @staticmethod
    def STREAMING_DATA_PREFIX():
        return ""
    
    @staticmethod
    def STREAMING_DONE_MARKER():
        return ""
    
    @staticmethod
    def CUSTOM_HEADERS():
        return {"X-API-Key": "test-key", "X-Version": "v1"}
    
    @staticmethod
    def REQUEST_TRANSFORM():
        return "none"
    
    @staticmethod
    def RESPONSE_TRANSFORM():
        return "none"
    
    @staticmethod
    def ADAPTER_DEBUG():
        return True


class TestConfigurableAdapter:
    """ConfigurableAdapterのテスト"""
    
    def test_transform_request_standard(self):
        """標準的なリクエスト変換のテスト"""
        adapter = ConfigurableAdapter(MockConfig)
        
        request = ChatCompletionRequest(
            model="gpt-3.5-turbo",
            messages=[
                ChatMessage(role="user", content="Hello"),
                ChatMessage(role="assistant", content="Hi there!")
            ],
            temperature=0.7,
            max_tokens=100,
            stream=True
        )
        
        result = adapter.transform_request(request)
        
        expected = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"}
            ],
            "temperature": 0.7,
            "max_tokens": 100,
            "stream": True
        }
        
        assert result == expected
    
    def test_transform_request_custom_fields(self):
        """カスタムフィールドでのリクエスト変換のテスト"""
        adapter = ConfigurableAdapter(CustomFieldConfig)
        
        request = ChatCompletionRequest(
            model="test-model",
            messages=[ChatMessage(role="user", content="Hello")],
            temperature=0.8,
            stream=True
        )
        
        result = adapter.transform_request(request)
        
        expected = {
            "engine": "test-model",
            "conversation": [{"role": "user", "content": "Hello"}],
            "randomness": 0.8,
            "streaming_mode": True
        }
        
        assert result == expected
    
    def test_transform_request_disabled_fields(self):
        """無効化されたフィールドのテスト"""
        config = Mock()
        config.REQUEST_MESSAGES_FIELD = Mock(return_value="messages")
        config.REQUEST_MODEL_FIELD = Mock(return_value="")  # 無効化
        config.REQUEST_TEMPERATURE_FIELD = Mock(return_value="")  # 無効化
        config.REQUEST_MAX_TOKENS_FIELD = Mock(return_value="")
        config.REQUEST_STREAM_FIELD = Mock(return_value="")
        config.REQUEST_STOP_FIELD = Mock(return_value="")
        config.REQUEST_TRANSFORM = Mock(return_value="none")
        config.ADAPTER_DEBUG = Mock(return_value=False)
        
        adapter = ConfigurableAdapter(config)
        
        request = ChatCompletionRequest(
            model="test-model",
            messages=[ChatMessage(role="user", content="Hello")],
            temperature=0.7,
            max_tokens=100
        )
        
        result = adapter.transform_request(request)
        
        # モデル、温度、最大トークン数は含まれない
        expected = {
            "messages": [{"role": "user", "content": "Hello"}]
        }
        
        assert result == expected
    
    def test_transform_response_standard(self):
        """標準的なレスポンス変換のテスト"""
        adapter = ConfigurableAdapter(MockConfig)
        
        server_response = {
            "content": "Hello, how can I help you?",
            "finish_reason": "stop",
            "model": "test-model",
            "created": 1234567890
        }
        
        original_request = ChatCompletionRequest(
            model="gpt-3.5-turbo",
            messages=[ChatMessage(role="user", content="Hello")]
        )
        
        result = adapter.transform_response(server_response, original_request)
        
        assert result.content == "Hello, how can I help you?"
        assert result.finish_reason == "stop"
    
    def test_transform_response_nested_fields(self):
        """ネストしたフィールドのレスポンス変換のテスト"""
        adapter = ConfigurableAdapter(CustomFieldConfig)
        
        server_response = {
            "response": {
                "text": "Nested response content",
                "status": "completed"
            },
            "metadata": {
                "timestamp": 1234567890
            }
        }
        
        original_request = ChatCompletionRequest(
            model="test-model",
            messages=[ChatMessage(role="user", content="Hello")]
        )
        
        result = adapter.transform_response(server_response, original_request)
        
        assert result.content == "Nested response content"
        assert result.finish_reason == "completed"
    
    def test_transform_response_missing_fields(self):
        """存在しないフィールドのレスポンス変換のテスト"""
        adapter = ConfigurableAdapter(MockConfig)
        
        server_response = {
            "other_field": "value"
        }
        
        original_request = ChatCompletionRequest(
            model="test-model",
            messages=[ChatMessage(role="user", content="Hello")]
        )
        
        result = adapter.transform_response(server_response, original_request)
        
        assert result.content == ""  # デフォルト値
        assert result.finish_reason == "stop"  # デフォルト値
    
    def test_parse_streaming_chunk_sse(self):
        """SSE形式のストリーミングチャンク解析のテスト"""
        adapter = ConfigurableAdapter(MockConfig)
        
        # データチャンク
        result = adapter.parse_streaming_chunk('data: {"content": "Hello", "finish_reason": null}')
        assert result["type"] == "data"
        assert result["data"]["content"] == "Hello"
        
        # 完了マーカー
        result = adapter.parse_streaming_chunk("data: [DONE]")
        assert result["type"] == "done"
        
        # 無効なJSON
        result = adapter.parse_streaming_chunk("data: {invalid json}")
        assert result["type"] == "error"
        
        # 空行
        result = adapter.parse_streaming_chunk("")
        assert result is None
    
    def test_parse_streaming_chunk_jsonlines(self):
        """JSON Lines形式のストリーミングチャンク解析のテスト"""
        config = Mock()
        config.STREAMING_FORMAT = Mock(return_value="jsonlines")
        config.ADAPTER_DEBUG = Mock(return_value=False)
        
        adapter = ConfigurableAdapter(config)
        
        # 有効なJSON
        result = adapter.parse_streaming_chunk('{"content": "Hello", "finish_reason": null}')
        assert result["type"] == "data"
        assert result["data"]["content"] == "Hello"
        
        # 無効なJSON
        result = adapter.parse_streaming_chunk("{invalid json}")
        assert result["type"] == "error"
    
    def test_get_custom_headers(self):
        """カスタムヘッダー取得のテスト"""
        adapter = ConfigurableAdapter(CustomFieldConfig)
        
        headers = adapter.get_custom_headers()
        expected = {"X-API-Key": "test-key", "X-Version": "v1"}
        
        assert headers == expected
    
    def test_supports_streaming(self):
        """ストリーミングサポートチェックのテスト"""
        # ストリーミング対応
        adapter = ConfigurableAdapter(MockConfig)
        assert adapter.supports_streaming() is True
        
        # ストリーミング非対応
        config = Mock()
        config.STREAMING_FORMAT = Mock(return_value="none")
        config.REQUEST_STREAM_FIELD = Mock(return_value="")
        adapter = ConfigurableAdapter(config)
        assert adapter.supports_streaming() is False


class TestAdapterFactory:
    """AdapterFactoryのテスト"""
    
    def test_create_adapter_default(self):
        """デフォルトアダプター作成のテスト"""
        adapter = AdapterFactory.create_adapter()
        assert isinstance(adapter, BaseAdapter)
    
    def test_create_adapter_with_config(self):
        """設定指定でのアダプター作成のテスト"""
        adapter = AdapterFactory.create_adapter(MockConfig)
        assert isinstance(adapter, ConfigurableAdapter)
        assert adapter.config == MockConfig
    
    def test_create_adapter_unknown_type(self):
        """不明なアダプタータイプでのエラーテスト"""
        config = Mock()
        config.ADAPTER_TYPE = Mock(return_value="unknown_adapter")
        
        with pytest.raises(ValueError, match="Unknown adapter type"):
            AdapterFactory.create_adapter(config)
    
    def test_register_adapter(self):
        """カスタムアダプター登録のテスト"""
        class CustomAdapter(BaseAdapter):
            def transform_request(self, request):
                return {}
            
            def transform_response(self, response, request):
                return ExistingServerResponse(content="", finish_reason="stop")
            
            def parse_streaming_chunk(self, chunk):
                return None
            
            def get_custom_headers(self):
                return {}
        
        AdapterFactory.register_adapter("custom_test", CustomAdapter)
        
        available = AdapterFactory.get_available_adapters()
        assert "custom_test" in available
        assert available["custom_test"] == CustomAdapter
    
    def test_validate_adapter_config_success(self):
        """アダプター設定検証成功のテスト"""
        with patch.object(MockConfig, 'validate'):
            result = AdapterFactory.validate_adapter_config(MockConfig)
            assert result is True
    
    def test_validate_adapter_config_failure(self):
        """アダプター設定検証失敗のテスト"""
        config = Mock()
        config.ADAPTER_TYPE = Mock(return_value="unknown")
        config.validate.side_effect = ValueError("Invalid config")
        
        result = AdapterFactory.validate_adapter_config(config)
        assert result is False
    
    def test_get_default_adapter(self):
        """デフォルトアダプター取得のテスト"""
        adapter = get_default_adapter()
        assert isinstance(adapter, BaseAdapter)