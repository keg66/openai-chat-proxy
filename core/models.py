"""
OpenAI API-compatible data model definitions
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union
import time
import uuid


@dataclass
class ChatMessage:
    """Chat message"""
    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class ChatCompletionRequest:
    """OpenAI /v1/chat/completions request"""
    model: str
    messages: List[ChatMessage]
    temperature: float = 1.0
    max_tokens: Optional[int] = None
    stream: bool = False
    stop: Optional[Union[str, List[str]]] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatCompletionRequest':
        """Create instance from dictionary"""
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
    """Chat completion choice"""
    index: int
    message: ChatMessage
    finish_reason: Optional[str] = None


@dataclass
class ChatCompletionUsage:
    """Token usage"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass
class ChatCompletionResponse:
    """OpenAI /v1/chat/completions response"""
    id: str = field(default_factory=lambda: f"chatcmpl-{uuid.uuid4().hex[:29]}")
    object: str = "chat.completion"
    created: int = field(default_factory=lambda: int(time.time()))
    model: str = ""
    choices: List[ChatCompletionChoice] = field(default_factory=list)
    usage: Optional[ChatCompletionUsage] = None


@dataclass
class ChatCompletionChunkDelta:
    """Streaming response delta"""
    content: Optional[str] = None
    role: Optional[str] = None


@dataclass
class ChatCompletionChunkChoice:
    """Streaming response choice"""
    index: int
    delta: ChatCompletionChunkDelta
    finish_reason: Optional[str] = None


@dataclass
class ChatCompletionChunk:
    """OpenAI streaming response chunk"""
    id: str = field(default_factory=lambda: f"chatcmpl-{uuid.uuid4().hex[:29]}")
    object: str = "chat.completion.chunk"
    created: int = field(default_factory=lambda: int(time.time()))
    model: str = ""
    choices: List[ChatCompletionChunkChoice] = field(default_factory=list)


@dataclass
class ExistingServerRequest:
    """Request format for existing server"""
    model: str
    messages: List[Dict[str, str]]
    temperature: float = 1.0
    max_tokens: Optional[int] = None
    stream: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
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
    """Response format from existing server"""
    content: str
    finish_reason: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExistingServerResponse':
        """Create instance from dictionary"""
        return cls(
            content=data.get("content", ""),
            finish_reason=data.get("finish_reason")
        )