"""
Base adapter class
Base class for providing compatibility with different existing servers
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Generator, Optional
import logging

from ..models import ChatCompletionRequest, ExistingServerRequest, ExistingServerResponse


class BaseAdapter(ABC):
    """Base class for adapters"""
    
    def __init__(self, config):
        """
        Args:
            config: Adapter configuration object
        """
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        if config.ADAPTER_DEBUG:
            self.logger.setLevel(logging.DEBUG)
    
    @abstractmethod
    def transform_request(self, openai_request: ChatCompletionRequest) -> Dict[str, Any]:
        """
        Transform OpenAI format request to existing server format
        
        Args:
            openai_request: OpenAI format request
            
        Returns:
            Dict: Request data for existing server
        """
        pass
    
    @abstractmethod
    def transform_response(self, server_response: Dict[str, Any], original_request: ChatCompletionRequest) -> ExistingServerResponse:
        """
        Transform existing server response to proxy format
        
        Args:
            server_response: Response from existing server
            original_request: Original OpenAI request
            
        Returns:
            ExistingServerResponse: Proxy format response
        """
        pass
    
    @abstractmethod
    def parse_streaming_chunk(self, chunk_line: str) -> Optional[Dict[str, Any]]:
        """
        Parse streaming response chunk
        
        Args:
            chunk_line: One line of streaming data
            
        Returns:
            Dict: Parsed chunk data, None if cannot parse
        """
        pass
    
    @abstractmethod
    def get_custom_headers(self) -> Dict[str, str]:
        """
        Get custom headers
        
        Returns:
            Dict: Custom header dictionary
        """
        pass
    
    def log_request_transform(self, openai_request: ChatCompletionRequest, transformed_request: Dict[str, Any]) -> None:
        """Log request transformation (for debugging)"""
        if self.config.ADAPTER_DEBUG:
            self.logger.debug("Request transformation:")
            self.logger.debug(f"  Original: model={openai_request.model}, messages_count={len(openai_request.messages)}, stream={openai_request.stream}")
            self.logger.debug(f"  Transformed: {transformed_request}")
    
    def log_response_transform(self, server_response: Dict[str, Any], transformed_response: ExistingServerResponse) -> None:
        """Log response transformation (for debugging)"""
        if self.config.ADAPTER_DEBUG:
            self.logger.debug("Response transformation:")
            self.logger.debug(f"  Server response keys: {list(server_response.keys())}")
            self.logger.debug(f"  Transformed: content_length={len(transformed_response.content)}, finish_reason={transformed_response.finish_reason}")


class AdapterError(Exception):
    """Adapter-related error"""
    pass


class UnsupportedFormatError(AdapterError):
    """Unsupported format error"""
    pass


class MappingError(AdapterError):
    """Field mapping error"""
    pass