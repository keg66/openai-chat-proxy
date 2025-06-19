"""
データモデルのテスト
"""
import pytest
from core.models import (
    ChatMessage, ChatCompletionRequest, ChatCompletionResponse,
    ChatCompletionChoice, ChatCompletionUsage, ExistingServerRequest,
    ExistingServerResponse
)


class TestChatMessage:
    """ChatMessageのテスト"""
    
    def test_create_chat_message(self):
        """ChatMessage作成のテスト"""
        message = ChatMessage(role="user", content="Hello")
        assert message.role == "user"
        assert message.content == "Hello"


class TestChatCompletionRequest:
    """ChatCompletionRequestのテスト"""
    
    def test_from_dict_minimal(self):
        """最小限のデータからの作成テスト"""
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "user", "content": "Hello"}
            ]
        }
        
        request = ChatCompletionRequest.from_dict(data)
        assert request.model == "gpt-3.5-turbo"
        assert len(request.messages) == 1
        assert request.messages[0].role == "user"
        assert request.messages[0].content == "Hello"
        assert request.temperature == 1.0
        assert request.stream is False
    
    def test_from_dict_full(self):
        """全パラメータでの作成テスト"""
        data = {
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": "Hello"}
            ],
            "temperature": 0.7,
            "max_tokens": 100,
            "stream": True,
            "stop": ["END"]
        }
        
        request = ChatCompletionRequest.from_dict(data)
        assert request.model == "gpt-4"
        assert len(request.messages) == 2
        assert request.temperature == 0.7
        assert request.max_tokens == 100
        assert request.stream is True
        assert request.stop == ["END"]


class TestExistingServerRequest:
    """ExistingServerRequestのテスト"""
    
    def test_to_dict(self):
        """辞書変換のテスト"""
        request = ExistingServerRequest(
            model="test-model",
            messages=[{"role": "user", "content": "test"}],
            temperature=0.8,
            max_tokens=50,
            stream=True
        )
        
        data = request.to_dict()
        expected = {
            "model": "test-model",
            "messages": [{"role": "user", "content": "test"}],
            "temperature": 0.8,
            "max_tokens": 50,
            "stream": True
        }
        
        assert data == expected
    
    def test_to_dict_without_max_tokens(self):
        """max_tokensがNoneの場合のテスト"""
        request = ExistingServerRequest(
            model="test-model",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=None
        )
        
        data = request.to_dict()
        assert "max_tokens" not in data


class TestExistingServerResponse:
    """ExistingServerResponseのテスト"""
    
    def test_from_dict(self):
        """辞書からの作成テスト"""
        data = {
            "content": "Hello, world!",
            "finish_reason": "stop"
        }
        
        response = ExistingServerResponse.from_dict(data)
        assert response.content == "Hello, world!"
        assert response.finish_reason == "stop"
    
    def test_from_dict_minimal(self):
        """最小限のデータでの作成テスト"""
        data = {"content": "test"}
        
        response = ExistingServerResponse.from_dict(data)
        assert response.content == "test"
        assert response.finish_reason is None


class TestChatCompletionResponse:
    """ChatCompletionResponseのテスト"""
    
    def test_default_values(self):
        """デフォルト値のテスト"""
        response = ChatCompletionResponse()
        assert response.object == "chat.completion"
        assert response.id.startswith("chatcmpl-")
        assert isinstance(response.created, int)
        assert response.choices == []
        assert response.usage is None