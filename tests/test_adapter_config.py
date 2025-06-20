"""
アダプター設定のテスト
"""
import pytest
import os
from unittest.mock import patch
from core.adapter_config import AdapterConfig, get_nested_value, set_nested_value


class TestAdapterConfig:
    """AdapterConfigクラスのテスト"""
    
    def test_default_values(self):
        """デフォルト値のテスト"""
        with patch.dict(os.environ, {}, clear=True):
            assert AdapterConfig.ADAPTER_TYPE() == "openai_compatible"
            assert AdapterConfig.REQUEST_MODEL_FIELD() == "model"
            assert AdapterConfig.REQUEST_MESSAGES_FIELD() == "messages"
            assert AdapterConfig.RESPONSE_CONTENT_FIELD() == "content"
            assert AdapterConfig.STREAMING_FORMAT() == "sse"
            assert AdapterConfig.ADAPTER_DEBUG() is False
    
    def test_environment_variable_override(self):
        """環境変数による設定上書きのテスト"""
        env_vars = {
            "ADAPTER_TYPE": "custom_server",
            "REQUEST_MODEL_FIELD": "engine",
            "REQUEST_MESSAGES_FIELD": "conversation",
            "REQUEST_TEMPERATURE_FIELD": "randomness",
            "RESPONSE_CONTENT_FIELD": "response.text",
            "RESPONSE_FINISH_FIELD": "status",
            "STREAMING_FORMAT": "jsonlines",
            "CUSTOM_HEADERS": '{"Authorization": "Bearer test-token"}',
            "ADAPTER_DEBUG": "true"
        }
        
        with patch.dict(os.environ, env_vars):
            assert AdapterConfig.ADAPTER_TYPE() == "custom_server"
            assert AdapterConfig.REQUEST_MODEL_FIELD() == "engine"
            assert AdapterConfig.REQUEST_MESSAGES_FIELD() == "conversation"
            assert AdapterConfig.REQUEST_TEMPERATURE_FIELD() == "randomness"
            assert AdapterConfig.RESPONSE_CONTENT_FIELD() == "response.text"
            assert AdapterConfig.RESPONSE_FINISH_FIELD() == "status"
            assert AdapterConfig.STREAMING_FORMAT() == "jsonlines"
            assert AdapterConfig.CUSTOM_HEADERS() == {"Authorization": "Bearer test-token"}
            assert AdapterConfig.ADAPTER_DEBUG() is True
    
    def test_validate_success(self):
        """設定検証成功のテスト"""
        with patch.dict(os.environ, {
            "REQUEST_MESSAGES_FIELD": "messages",
            "RESPONSE_CONTENT_FIELD": "content",
            "STREAMING_FORMAT": "sse"
        }):
            # 例外が発生しないことを確認
            AdapterConfig.validate()
    
    def test_validate_missing_required_field(self):
        """必須フィールド不足の検証エラーのテスト"""
        with patch.dict(os.environ, {"REQUEST_MESSAGES_FIELD": ""}):
            with pytest.raises(ValueError, match="REQUEST_MESSAGES_FIELD is required"):
                AdapterConfig.validate()
        
        with patch.dict(os.environ, {"RESPONSE_CONTENT_FIELD": ""}):
            with pytest.raises(ValueError, match="RESPONSE_CONTENT_FIELD is required"):
                AdapterConfig.validate()
    
    def test_validate_invalid_streaming_format(self):
        """無効なストリーミング形式の検証エラーのテスト"""
        with patch.dict(os.environ, {"STREAMING_FORMAT": "invalid_format"}):
            with pytest.raises(ValueError, match="Invalid STREAMING_FORMAT"):
                AdapterConfig.validate()
    
    def test_validate_invalid_custom_headers(self):
        """無効なカスタムヘッダーの検証エラーのテスト"""
        with patch.dict(os.environ, {"CUSTOM_HEADERS": "invalid json"}):
            with pytest.raises(ValueError, match="CUSTOM_HEADERS must be a valid JSON object"):
                AdapterConfig.validate()
    
    def test_get_adapter_info(self):
        """アダプター情報取得のテスト"""
        with patch.dict(os.environ, {
            "ADAPTER_TYPE": "test_adapter",
            "REQUEST_MODEL_FIELD": "engine",
            "RESPONSE_CONTENT_FIELD": "response.text",
            "CUSTOM_HEADERS": '{"X-API-Key": "test"}'
        }):
            info = AdapterConfig.get_adapter_info()
            
            assert info["adapter_type"] == "test_adapter"
            assert info["request_mapping"]["model"] == "engine"
            assert info["response_mapping"]["content"] == "response.text"
            assert info["custom_headers"] == {"X-API-Key": "test"}
    
    def test_get_adapter_info_with_disabled_fields(self):
        """無効化されたフィールドのアダプター情報取得のテスト"""
        with patch.dict(os.environ, {
            "REQUEST_MODEL_FIELD": "",
            "RESPONSE_FINISH_FIELD": ""
        }):
            info = AdapterConfig.get_adapter_info()
            
            assert info["request_mapping"]["model"] is None
            assert info["response_mapping"]["finish_reason"] is None


class TestNestedValueFunctions:
    """ネストした値の操作関数のテスト"""
    
    def test_get_nested_value_simple(self):
        """シンプルな値取得のテスト"""
        data = {"key": "value"}
        assert get_nested_value(data, "key") == "value"
        assert get_nested_value(data, "nonexistent") is None
    
    def test_get_nested_value_nested(self):
        """ネストした値取得のテスト"""
        data = {
            "response": {
                "choices": [
                    {"message": {"content": "Hello, world!"}}
                ]
            }
        }
        
        assert get_nested_value(data, "response.choices[0].message.content") == "Hello, world!"
        assert get_nested_value(data, "response.choices[1].message.content") is None
        assert get_nested_value(data, "response.nonexistent") is None
    
    def test_get_nested_value_edge_cases(self):
        """エッジケースのテスト"""
        data = {"key": "value"}
        
        assert get_nested_value(None, "key") is None
        assert get_nested_value(data, "") is None
        assert get_nested_value(data, None) is None
        assert get_nested_value({}, "key") is None
    
    def test_set_nested_value_simple(self):
        """シンプルな値設定のテスト"""
        data = {}
        set_nested_value(data, "key", "value")
        assert data == {"key": "value"}
    
    def test_set_nested_value_nested(self):
        """ネストした値設定のテスト"""
        data = {}
        set_nested_value(data, "response.message.content", "Hello")
        
        expected = {
            "response": {
                "message": {
                    "content": "Hello"
                }
            }
        }
        assert data == expected
    
    def test_set_nested_value_overwrite(self):
        """既存値の上書きテスト"""
        data = {"response": {"message": {"content": "Old"}}}
        set_nested_value(data, "response.message.content", "New")
        assert data["response"]["message"]["content"] == "New"
    
    def test_set_nested_value_edge_cases(self):
        """エッジケースのテスト"""
        data = {}
        
        # 空のフィールドパス
        set_nested_value(data, "", "value")
        assert data == {}
        
        # Noneのフィールドパス
        set_nested_value(data, None, "value")
        assert data == {}