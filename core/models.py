"""
OpenAI API互換のデータモデル定義
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union
import time
import uuid


@dataclass
class ChatMessage:
    """チャットメッセージ"""
    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class ChatCompletionRequest:
    """OpenAI /v1/chat/completions リクエスト"""
    model: str
    messages: List[ChatMessage]
    temperature: float = 1.0
    max_tokens: Optional[int] = None
    stream: bool = False
    stop: Optional[Union[str, List[str]]] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatCompletionRequest':
        """辞書からインスタンスを生成"""
        messages = [
            ChatMessage(role=msg["role"], content=msg["content"])
            for msg in data["messages"]
        ]
        return cls(
            model=data["model"],
            messages=messages,
            temperature=data.get("temperature", 1.0),
            max_tokens=data.get("max_tokens"),
            stream=data.get("stream", False),
            stop=data.get("stop")
        )


@dataclass
class ChatCompletionChoice:
    """チャット完了の選択肢"""
    index: int
    message: ChatMessage
    finish_reason: Optional[str] = None


@dataclass
class ChatCompletionUsage:
    """トークン使用量"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass
class ChatCompletionResponse:
    """OpenAI /v1/chat/completions レスポンス"""
    id: str = field(default_factory=lambda: f"chatcmpl-{uuid.uuid4().hex[:29]}")
    object: str = "chat.completion"
    created: int = field(default_factory=lambda: int(time.time()))
    model: str = ""
    choices: List[ChatCompletionChoice] = field(default_factory=list)
    usage: Optional[ChatCompletionUsage] = None


@dataclass
class ChatCompletionChunkDelta:
    """ストリーミングレスポンスのデルタ"""
    content: Optional[str] = None
    role: Optional[str] = None


@dataclass
class ChatCompletionChunkChoice:
    """ストリーミングレスポンスの選択肢"""
    index: int
    delta: ChatCompletionChunkDelta
    finish_reason: Optional[str] = None


@dataclass
class ChatCompletionChunk:
    """OpenAI ストリーミングレスポンスのチャンク"""
    id: str = field(default_factory=lambda: f"chatcmpl-{uuid.uuid4().hex[:29]}")
    object: str = "chat.completion.chunk"
    created: int = field(default_factory=lambda: int(time.time()))
    model: str = ""
    choices: List[ChatCompletionChunkChoice] = field(default_factory=list)


@dataclass
class ExistingServerRequest:
    """既存サーバー向けのリクエスト形式"""
    model: str
    messages: List[Dict[str, str]]
    temperature: float = 1.0
    max_tokens: Optional[int] = None
    stream: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        data = {
            "model": self.model,
            "messages": [{"role": msg["role"], "content": msg["content"]} for msg in self.messages],
            "temperature": self.temperature,
            "stream": self.stream
        }
        if self.max_tokens is not None:
            data["max_tokens"] = self.max_tokens
        return data


@dataclass
class ExistingServerResponse:
    """既存サーバーからのレスポンス形式"""
    content: str
    finish_reason: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExistingServerResponse':
        """辞書からインスタンスを生成"""
        return cls(
            content=data.get("content", ""),
            finish_reason=data.get("finish_reason")
        )