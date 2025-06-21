"""
Existing server communication client with adapter functionality
"""
import requests
import json
import logging
from typing import Dict, Any, Generator, Optional
from requests.exceptions import RequestException, Timeout, ConnectionError
from .models import ExistingServerRequest, ExistingServerResponse
from .converter import DataConverter
from .adapters.base import BaseAdapter
from .adapters.factory import get_default_adapter


class ExistingServerClient:
    """Client for communicating with existing servers with adapter functionality"""
    
    def __init__(self, server_url: str, timeout: int = 30, adapter: Optional[BaseAdapter] = None):
        """
        Args:
            server_url: Existing server URL
            timeout: Request timeout (seconds)
            adapter: Adapter to use (default adapter used if None)
        """
        self.server_url = server_url
        self.timeout = timeout
        self.adapter = adapter or get_default_adapter()
        self.logger = logging.getLogger(__name__)
        
        # Initialize data converter with adapter
        self.converter = DataConverter(self.adapter)
    
    def send_request_dict(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send dictionary format request to existing server
        
        Args:
            request_data: Request data to send
            
        Returns:
            Dict: Response from server
        """
        try:
            self.logger.debug(f"Sending request to {self.server_url}")
            self.logger.debug(f"Request data: {request_data}")
            
            # Get custom headers
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            headers.update(self.converter.get_custom_headers())
            
            response = requests.post(
                self.server_url,
                json=request_data,
                timeout=self.timeout,
                headers=headers
            )
            
            response.raise_for_status()
            
            response_data = response.json()
            self.logger.debug(f"Response data: {response_data}")
            
            return response_data
            
        except ConnectionError as e:
            self.logger.error(f"Connection error: {e}")
            raise ConnectionError(f"Failed to connect to existing server: {e}")
        
        except Timeout as e:
            self.logger.error(f"Request timeout: {e}")
            raise Timeout(f"Request to existing server timed out after {self.timeout} seconds")
        
        except requests.HTTPError as e:
            self.logger.error(f"HTTP error: {e}")
            raise RequestException(f"HTTP error from existing server: {e}")
        
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error: {e}")
            raise RequestException(f"Invalid JSON response from existing server: {e}")
        
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise RequestException(f"Unexpected error: {e}")
    
    # Method for backward compatibility
    def send_request(self, request: ExistingServerRequest) -> ExistingServerResponse:
        """
        Send non-streaming request to existing server
        
        Args:
            request: Request to send
            
        Returns:
            ExistingServerResponse: Response from server
            
        Raises:
            ConnectionError: When unable to connect to server
            Timeout: When request times out
            RequestException: Other HTTP errors
        """
        try:
            self.logger.debug(f"Sending request to {self.server_url}")
            self.logger.debug(f"Request data: {request.to_dict()}")
            
            response = requests.post(
                self.server_url,
                json=request.to_dict(),
                timeout=self.timeout,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            )
            
            response.raise_for_status()
            
            response_data = response.json()
            self.logger.debug(f"Response data: {response_data}")
            
            return ExistingServerResponse.from_dict(response_data)
            
        except ConnectionError as e:
            self.logger.error(f"Connection error: {e}")
            raise ConnectionError(f"Failed to connect to existing server: {e}")
        
        except Timeout as e:
            self.logger.error(f"Request timeout: {e}")
            raise Timeout(f"Request to existing server timed out after {self.timeout} seconds")
        
        except requests.HTTPError as e:
            self.logger.error(f"HTTP error: {e}")
            raise RequestException(f"HTTP error from existing server: {e}")
        
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error: {e}")
            raise RequestException(f"Invalid JSON response from existing server: {e}")
        
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise RequestException(f"Unexpected error: {e}")
    
    def send_streaming_request_dict(self, request_data: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
        """
        Send dictionary format streaming request to existing server
        
        Args:
            request_data: Request data to send
            
        Yields:
            Dict: Streaming response from server
        """
        try:
            self.logger.debug(f"Sending streaming request to {self.server_url}")
            self.logger.debug(f"Request data: {request_data}")
            
            # Get custom headers
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'text/event-stream'
            }
            headers.update(self.converter.get_custom_headers())
            
            response = requests.post(
                self.server_url,
                json=request_data,
                timeout=self.timeout,
                stream=True,
                headers=headers
            )
            
            response.raise_for_status()
            
            # Process streaming response
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    parsed_line = self.converter.parse_streaming_chunk(line)
                    
                    if parsed_line and parsed_line.get("type") == "data":
                        yield parsed_line["data"]
                    elif parsed_line and parsed_line.get("type") == "done":
                        break
                    elif parsed_line and parsed_line.get("type") == "error":
                        self.logger.error(f"Streaming parsing error: {parsed_line['error']}")
                        raise RequestException(f"Streaming parsing error: {parsed_line['error']}")
                        
        except ConnectionError as e:
            self.logger.error(f"Connection error: {e}")
            raise ConnectionError(f"Failed to connect to existing server: {e}")
        
        except Timeout as e:
            self.logger.error(f"Request timeout: {e}")
            raise Timeout(f"Streaming request to existing server timed out after {self.timeout} seconds")
        
        except requests.HTTPError as e:
            self.logger.error(f"HTTP error: {e}")
            raise RequestException(f"HTTP error from existing server: {e}")
        
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise RequestException(f"Unexpected error in streaming request: {e}")
    
    # Method for backward compatibility
    def send_streaming_request(self, request: ExistingServerRequest) -> Generator[Dict[str, Any], None, None]:
        """
        Send streaming request to existing server
        
        Args:
            request: Request to send
            
        Yields:
            Dict[str, Any]: Streaming response from server
            
        Raises:
            ConnectionError: When unable to connect to server
            Timeout: When request times out
            RequestException: Other HTTP errors
        """
        try:
            self.logger.debug(f"Sending streaming request to {self.server_url}")
            self.logger.debug(f"Request data: {request.to_dict()}")
            
            response = requests.post(
                self.server_url,
                json=request.to_dict(),
                timeout=self.timeout,
                stream=True,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'text/event-stream'
                }
            )
            
            response.raise_for_status()
            
            # Process streaming response
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    parsed_line = DataConverter.parse_sse_line(line)
                    
                    if parsed_line["type"] == "data":
                        yield parsed_line["data"]
                    elif parsed_line["type"] == "done":
                        break
                    elif parsed_line["type"] == "error":
                        self.logger.error(f"SSE parsing error: {parsed_line['error']}")
                        raise RequestException(f"SSE parsing error: {parsed_line['error']}")
                        
        except ConnectionError as e:
            self.logger.error(f"Connection error: {e}")
            raise ConnectionError(f"Failed to connect to existing server: {e}")
        
        except Timeout as e:
            self.logger.error(f"Request timeout: {e}")
            raise Timeout(f"Streaming request to existing server timed out after {self.timeout} seconds")
        
        except requests.HTTPError as e:
            self.logger.error(f"HTTP error: {e}")
            raise RequestException(f"HTTP error from existing server: {e}")
        
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise RequestException(f"Unexpected error in streaming request: {e}")
    
    def health_check(self) -> bool:
        """
        Health check for existing server
        
        Returns:
            bool: True if server responds normally
        """
        try:
            # Send simple test request
            test_request = ExistingServerRequest(
                model="test",
                messages=[{"role": "user", "content": "health check"}],
                stream=False
            )
            
            response = requests.post(
                self.server_url,
                json=test_request.to_dict(),
                timeout=5,  # Short timeout for health check
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            )
            
            return response.status_code == 200
            
        except Exception as e:
            self.logger.warning(f"Health check failed: {e}")
            return False
    
    def get_server_info(self) -> Dict[str, Any]:
        """
        Get server information
        
        Returns:
            Dict[str, Any]: Server information
        """
        return {
            "server_url": self.server_url,
            "timeout": self.timeout,
            "health": self.health_check()
        }