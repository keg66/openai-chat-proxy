"""
Configurable adapter
Supports various existing servers through environment variable configuration
"""
import json
from typing import Dict, Any, Optional, List
from .base import BaseAdapter, MappingError, UnsupportedFormatError
from ..adapter_config import get_nested_value, set_nested_value
from ..models import ChatCompletionRequest, ExistingServerResponse, ChatMessage


class ConfigurableAdapter(BaseAdapter):
    """Configurable adapter"""
    
    def transform_request(self, openai_request: ChatCompletionRequest) -> Dict[str, Any]:
        """Convert OpenAI format request to existing server format"""
        request_data = {}
        
        try:
            # Message field (required)
            if self.config.REQUEST_MESSAGES_FIELD():
                messages = self._transform_messages(openai_request.messages)
                set_nested_value(request_data, self.config.REQUEST_MESSAGES_FIELD(), messages)
            else:
                raise MappingError("REQUEST_MESSAGES_FIELD is required")
            
            # Model field (optional)
            if self.config.REQUEST_MODEL_FIELD() and openai_request.model:
                set_nested_value(request_data, self.config.REQUEST_MODEL_FIELD(), openai_request.model)
            
            # Temperature setting (optional, only if not default value)
            if self.config.REQUEST_TEMPERATURE_FIELD() and openai_request.temperature != 1.0:
                set_nested_value(request_data, self.config.REQUEST_TEMPERATURE_FIELD(), openai_request.temperature)
            
            # Maximum token count (optional)
            if self.config.REQUEST_MAX_TOKENS_FIELD() and openai_request.max_tokens:
                set_nested_value(request_data, self.config.REQUEST_MAX_TOKENS_FIELD(), openai_request.max_tokens)
            
            # Streaming setting (optional)
            if self.config.REQUEST_STREAM_FIELD() and openai_request.stream:
                set_nested_value(request_data, self.config.REQUEST_STREAM_FIELD(), openai_request.stream)
            
            # Stop strings (optional)
            if self.config.REQUEST_STOP_FIELD() and openai_request.stop:
                set_nested_value(request_data, self.config.REQUEST_STOP_FIELD(), openai_request.stop)
            
            self.log_request_transform(openai_request, request_data)
            return request_data
            
        except Exception as e:
            raise MappingError(f"Failed to transform request: {str(e)}")
    
    def transform_response(self, server_response: Dict[str, Any], original_request: ChatCompletionRequest) -> ExistingServerResponse:
        """Convert existing server response to proxy format"""
        try:
            # コンテンツフィールド（必須）
            content = get_nested_value(server_response, self.config.RESPONSE_CONTENT_FIELD())
            if content is None:
                content = ""
                self.logger.warning(f"Content field '{self.config.RESPONSE_CONTENT_FIELD()}' not found in response")
            
            # 完了理由フィールド（オプション）
            finish_reason = None  # ストリーミング用にNoneで初期化
            if self.config.RESPONSE_FINISH_FIELD():
                server_finish_reason = get_nested_value(server_response, self.config.RESPONSE_FINISH_FIELD())
                if server_finish_reason is not None:
                    finish_reason = str(server_finish_reason)
            
            # 非ストリーミングレスポンスでfinish_reasonがNoneの場合のみデフォルトを使用
            if finish_reason is None and (not hasattr(original_request, 'stream') or not original_request.stream):
                finish_reason = "stop"
            
            # Model field (optional)
            model = original_request.model  # デフォルトは元のリクエストのモデル
            if self.config.RESPONSE_MODEL_FIELD():
                server_model = get_nested_value(server_response, self.config.RESPONSE_MODEL_FIELD())
                if server_model:
                    model = str(server_model)
            
            response = ExistingServerResponse(
                content=str(content),
                finish_reason=finish_reason
            )
            
            self.log_response_transform(server_response, response)
            return response
            
        except Exception as e:
            raise MappingError(f"Failed to transform response: {str(e)}")
    
    def parse_streaming_chunk(self, chunk_line: str) -> Optional[Dict[str, Any]]:
        """ストリーミングレスポンスのチャンクを解析"""
        if not chunk_line.strip():
            return None
        
        try:
            if self.config.STREAMING_FORMAT() == "sse":
                return self._parse_sse_chunk(chunk_line)
            elif self.config.STREAMING_FORMAT() == "jsonlines":
                return self._parse_jsonlines_chunk(chunk_line)
            elif self.config.STREAMING_FORMAT() == "none":
                return None
            else:
                raise UnsupportedFormatError(f"Unsupported streaming format: {self.config.STREAMING_FORMAT()}")
                
        except Exception as e:
            self.logger.warning(f"Failed to parse streaming chunk: {e}")
            return None
    
    def get_custom_headers(self) -> Dict[str, str]:
        """カスタムヘッダーを取得"""
        return self.config.CUSTOM_HEADERS().copy()
    
    def _transform_messages(self, messages: List[ChatMessage]) -> List[Dict[str, str]]:
        """メッセージを変換"""
        if self.config.REQUEST_TRANSFORM() == "flatten_messages":
            # メッセージを単一のプロンプトに変換
            return self._flatten_messages_to_prompt(messages)
        elif self.config.REQUEST_TRANSFORM() == "none":
            # 標準形式のまま
            return [{"role": msg.role, "content": msg.content} for msg in messages]
        else:
            # その他の変換は今後実装
            return [{"role": msg.role, "content": msg.content} for msg in messages]
    
    def _flatten_messages_to_prompt(self, messages: List[ChatMessage]) -> str:
        """メッセージ配列を単一のプロンプト文字列に変換"""
        prompt_parts = []
        
        for msg in messages:
            if msg.role == "system":
                prompt_parts.append(f"System: {msg.content}")
            elif msg.role == "user":
                prompt_parts.append(f"Human: {msg.content}")
            elif msg.role == "assistant":
                prompt_parts.append(f"Assistant: {msg.content}")
        
        return "\n\n".join(prompt_parts)
    
    def _parse_sse_chunk(self, chunk_line: str) -> Optional[Dict[str, Any]]:
        """Server-Sent Events形式のチャンクを解析"""
        line = chunk_line.strip()
        
        if line.startswith(self.config.STREAMING_DATA_PREFIX()):
            data_str = line[len(self.config.STREAMING_DATA_PREFIX()):]
            
            if data_str == self.config.STREAMING_DONE_MARKER():
                return {"type": "done"}
            
            try:
                data = json.loads(data_str)
                return {"type": "data", "data": data}
            except json.JSONDecodeError as e:
                self.logger.warning(f"Invalid JSON in SSE chunk: {data_str}")
                return {"type": "error", "error": f"Invalid JSON: {str(e)}"}
        
        elif line.startswith("event: "):
            return {"type": "event", "event": line[7:]}
        elif line.startswith("id: "):
            return {"type": "id", "id": line[4:]}
        elif line == "":
            return {"type": "empty"}
        else:
            return {"type": "unknown", "line": line}
    
    def _parse_jsonlines_chunk(self, chunk_line: str) -> Optional[Dict[str, Any]]:
        """JSON Lines形式のチャンクを解析"""
        try:
            data = json.loads(chunk_line.strip())
            return {"type": "data", "data": data}
        except json.JSONDecodeError as e:
            self.logger.warning(f"Invalid JSON in JSONL chunk: {chunk_line}")
            return {"type": "error", "error": f"Invalid JSON: {str(e)}"}
    
    def supports_streaming(self) -> bool:
        """ストリーミングをサポートしているかチェック"""
        return (
            self.config.STREAMING_FORMAT() != "none" and
            bool(self.config.REQUEST_STREAM_FIELD())
        )
    
    def get_adapter_type(self) -> str:
        """アダプタータイプを取得"""
        return self.config.ADAPTER_TYPE()