"""
データ変換ロジック
OpenAI形式と既存サーバー形式の間でデータを変換
"""
import json
from typing import Dict, Any, Generator, List
from .models import (
    ChatCompletionRequest, ChatCompletionResponse, ChatCompletionChoice,
    ChatCompletionChunk, ChatCompletionChunkChoice, ChatCompletionChunkDelta,
    ChatCompletionUsage, ChatMessage, ExistingServerRequest, ExistingServerResponse
)


class DataConverter:
    """データ変換クラス"""
    
    @staticmethod
    def openai_to_existing_server(request: ChatCompletionRequest) -> ExistingServerRequest:
        """OpenAI形式のリクエストを既存サーバー形式に変換"""
        messages = []
        for msg in request.messages:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        return ExistingServerRequest(
            model=request.model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=request.stream
        )
    
    @staticmethod
    def existing_server_to_openai(
        server_response: ExistingServerResponse,
        original_request: ChatCompletionRequest
    ) -> ChatCompletionResponse:
        """既存サーバーのレスポンスをOpenAI形式に変換"""
        choice = ChatCompletionChoice(
            index=0,
            message=ChatMessage(
                role="assistant",
                content=server_response.content
            ),
            finish_reason=server_response.finish_reason or "stop"
        )
        
        # 簡易的なトークン数計算（実際の実装では適切なトークナイザーを使用）
        prompt_tokens = DataConverter._estimate_tokens(original_request.messages)
        completion_tokens = DataConverter._estimate_tokens([ChatMessage(role="assistant", content=server_response.content)])
        
        usage = ChatCompletionUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens
        )
        
        return ChatCompletionResponse(
            model=original_request.model,
            choices=[choice],
            usage=usage
        )
    
    @staticmethod
    def create_streaming_chunk(
        content: str,
        finish_reason: str = None,
        model: str = "",
        chunk_id: str = None
    ) -> ChatCompletionChunk:
        """ストリーミング用のチャンクを作成"""
        delta = ChatCompletionChunkDelta(content=content)
        if finish_reason == "start":
            delta.role = "assistant"
            delta.content = ""
        
        choice = ChatCompletionChunkChoice(
            index=0,
            delta=delta,
            finish_reason=finish_reason if finish_reason not in ["start", None] else None
        )
        
        chunk = ChatCompletionChunk(
            model=model,
            choices=[choice]
        )
        
        if chunk_id:
            chunk.id = chunk_id
        
        return chunk
    
    @staticmethod
    def parse_sse_line(line: str) -> Dict[str, Any]:
        """Server-Sent Eventsの行を解析"""
        line = line.strip()
        if line.startswith("data: "):
            data_str = line[6:]  # "data: "を除去
            if data_str == "[DONE]":
                return {"type": "done"}
            try:
                return {"type": "data", "data": json.loads(data_str)}
            except json.JSONDecodeError:
                return {"type": "error", "error": f"Invalid JSON: {data_str}"}
        elif line.startswith("event: "):
            return {"type": "event", "event": line[7:]}
        elif line.startswith("id: "):
            return {"type": "id", "id": line[4:]}
        elif line == "":
            return {"type": "empty"}
        else:
            return {"type": "unknown", "line": line}
    
    @staticmethod
    def format_sse_chunk(chunk: ChatCompletionChunk) -> str:
        """チャンクをSSE形式の文字列に変換"""
        data = {
            "id": chunk.id,
            "object": chunk.object,
            "created": chunk.created,
            "model": chunk.model,
            "choices": []
        }
        
        for choice in chunk.choices:
            choice_data = {
                "index": choice.index,
                "delta": {}
            }
            
            if choice.delta.role:
                choice_data["delta"]["role"] = choice.delta.role
            if choice.delta.content:
                choice_data["delta"]["content"] = choice.delta.content
            if choice.finish_reason:
                choice_data["finish_reason"] = choice.finish_reason
            
            data["choices"].append(choice_data)
        
        return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
    
    @staticmethod
    def _estimate_tokens(messages: List[ChatMessage]) -> int:
        """トークン数を概算（実際の実装では適切なトークナイザーを使用）"""
        total_chars = sum(len(msg.content) + len(msg.role) for msg in messages)
        # 大まかな推定：英語では4文字≈1トークン、日本語では2文字≈1トークン
        # ここでは簡易的に3文字≈1トークンとして計算
        return max(1, total_chars // 3)
    
    @staticmethod
    def create_error_response(
        error_message: str,
        error_type: str = "invalid_request_error",
        error_code: str = None
    ) -> Dict[str, Any]:
        """エラーレスポンスを作成"""
        error_data = {
            "message": error_message,
            "type": error_type
        }
        
        if error_code:
            error_data["code"] = error_code
        
        return {
            "error": error_data
        }