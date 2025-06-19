"""
データ変換機能のテスト
"""
import pytest
import json
from core.converter import DataConverter
from core.models import (
    ChatCompletionRequest, ChatMessage, ExistingServerResponse,
    ChatCompletionChunk
)


class TestDataConverter:
    """DataConverterのテスト"""
    
    def test_openai_to_existing_server(self):
        """OpenAI形式から既存サーバー形式への変換テスト"""
        # テストデータ作成
        request_data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are helpful"},
                {"role": "user", "content": "Hello"}
            ],
            "temperature": 0.7,
            "max_tokens": 100,
            "stream": True
        }
        
        openai_request = ChatCompletionRequest.from_dict(request_data)
        existing_request = DataConverter.openai_to_existing_server(openai_request)
        
        # 変換結果の検証
        assert existing_request.model == "gpt-3.5-turbo"
        assert len(existing_request.messages) == 2
        assert existing_request.messages[0]["role"] == "system"
        assert existing_request.messages[0]["content"] == "You are helpful"
        assert existing_request.messages[1]["role"] == "user"
        assert existing_request.messages[1]["content"] == "Hello"
        assert existing_request.temperature == 0.7
        assert existing_request.max_tokens == 100
        assert existing_request.stream is True
    
    def test_existing_server_to_openai(self):
        """既存サーバー形式からOpenAI形式への変換テスト"""
        # テストデータ作成
        server_response = ExistingServerResponse(
            content="Hello, how can I help you?",
            finish_reason="stop"
        )
        
        original_request = ChatCompletionRequest(
            model="gpt-3.5-turbo",
            messages=[
                ChatMessage(role="user", content="Hello")
            ]
        )
        
        # 変換実行
        openai_response = DataConverter.existing_server_to_openai(
            server_response, original_request
        )
        
        # 変換結果の検証
        assert openai_response.model == "gpt-3.5-turbo"
        assert openai_response.object == "chat.completion"
        assert len(openai_response.choices) == 1
        
        choice = openai_response.choices[0]
        assert choice.index == 0
        assert choice.message.role == "assistant"
        assert choice.message.content == "Hello, how can I help you?"
        assert choice.finish_reason == "stop"
        
        # 使用量の検証
        assert openai_response.usage is not None
        assert openai_response.usage.prompt_tokens > 0
        assert openai_response.usage.completion_tokens > 0
        assert openai_response.usage.total_tokens > 0
    
    def test_create_streaming_chunk(self):
        """ストリーミングチャンク作成のテスト"""
        chunk = DataConverter.create_streaming_chunk(
            content="Hello",
            finish_reason=None,
            model="gpt-3.5-turbo",
            chunk_id="test-chunk-id"
        )
        
        assert chunk.id == "test-chunk-id"
        assert chunk.object == "chat.completion.chunk"
        assert chunk.model == "gpt-3.5-turbo"
        assert len(chunk.choices) == 1
        
        choice = chunk.choices[0]
        assert choice.index == 0
        assert choice.delta.content == "Hello"
        assert choice.finish_reason is None
    
    def test_create_streaming_chunk_start(self):
        """開始チャンクの作成テスト"""
        chunk = DataConverter.create_streaming_chunk(
            content="",
            finish_reason="start",
            model="gpt-3.5-turbo"
        )
        
        choice = chunk.choices[0]
        assert choice.delta.role == "assistant"
        assert choice.delta.content == ""
        assert choice.finish_reason is None
    
    def test_parse_sse_line_data(self):
        """SSE行解析（データ）のテスト"""
        line = 'data: {"content": "Hello", "finish_reason": null}'
        result = DataConverter.parse_sse_line(line)
        
        assert result["type"] == "data"
        assert result["data"]["content"] == "Hello"
        assert result["data"]["finish_reason"] is None
    
    def test_parse_sse_line_done(self):
        """SSE行解析（完了）のテスト"""
        line = "data: [DONE]"
        result = DataConverter.parse_sse_line(line)
        
        assert result["type"] == "done"
    
    def test_parse_sse_line_invalid_json(self):
        """SSE行解析（無効なJSON）のテスト"""
        line = "data: {invalid json}"
        result = DataConverter.parse_sse_line(line)
        
        assert result["type"] == "error"
        assert "Invalid JSON" in result["error"]
    
    def test_format_sse_chunk(self):
        """SSE形式チャンク変換のテスト"""
        chunk = DataConverter.create_streaming_chunk(
            content="Hello",
            model="gpt-3.5-turbo"
        )
        
        sse_string = DataConverter.format_sse_chunk(chunk)
        
        assert sse_string.startswith("data: ")
        assert sse_string.endswith("\n\n")
        
        # JSONの有効性を確認
        json_str = sse_string[6:-2]  # "data: "と"\n\n"を除去
        data = json.loads(json_str)
        
        assert data["object"] == "chat.completion.chunk"
        assert data["model"] == "gpt-3.5-turbo"
        assert len(data["choices"]) == 1
        assert data["choices"][0]["delta"]["content"] == "Hello"
    
    def test_estimate_tokens(self):
        """トークン数推定のテスト"""
        messages = [
            ChatMessage(role="user", content="Hello world"),
            ChatMessage(role="assistant", content="Hi there!")
        ]
        
        tokens = DataConverter._estimate_tokens(messages)
        assert tokens > 0
        assert isinstance(tokens, int)
    
    def test_create_error_response(self):
        """エラーレスポンス作成のテスト"""
        error_response = DataConverter.create_error_response(
            error_message="Test error",
            error_type="test_error",
            error_code="TEST001"
        )
        
        assert "error" in error_response
        error_data = error_response["error"]
        assert error_data["message"] == "Test error"
        assert error_data["type"] == "test_error"
        assert error_data["code"] == "TEST001"
    
    def test_create_error_response_minimal(self):
        """最小限のエラーレスポンス作成のテスト"""
        error_response = DataConverter.create_error_response("Simple error")
        
        assert "error" in error_response
        error_data = error_response["error"]
        assert error_data["message"] == "Simple error"
        assert error_data["type"] == "invalid_request_error"
        assert "code" not in error_data