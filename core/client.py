"""
既存サーバー通信クライアント
"""
import requests
import json
import logging
from typing import Dict, Any, Generator, Optional
from requests.exceptions import RequestException, Timeout, ConnectionError
from .models import ExistingServerRequest, ExistingServerResponse
from .converter import DataConverter


class ExistingServerClient:
    """既存サーバーとの通信を行うクライアント"""
    
    def __init__(self, server_url: str, timeout: int = 30):
        """
        Args:
            server_url: 既存サーバーのURL
            timeout: リクエストタイムアウト（秒）
        """
        self.server_url = server_url
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
    
    def send_request(self, request: ExistingServerRequest) -> ExistingServerResponse:
        """
        既存サーバーに非ストリーミングリクエストを送信
        
        Args:
            request: 送信するリクエスト
            
        Returns:
            ExistingServerResponse: サーバーからのレスポンス
            
        Raises:
            ConnectionError: サーバーに接続できない場合
            Timeout: リクエストがタイムアウトした場合
            RequestException: その他のHTTPエラー
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
    
    def send_streaming_request(self, request: ExistingServerRequest) -> Generator[Dict[str, Any], None, None]:
        """
        既存サーバーにストリーミングリクエストを送信
        
        Args:
            request: 送信するリクエスト
            
        Yields:
            Dict[str, Any]: サーバーからのストリーミングレスポンス
            
        Raises:
            ConnectionError: サーバーに接続できない場合
            Timeout: リクエストがタイムアウトした場合
            RequestException: その他のHTTPエラー
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
            
            # ストリーミングレスポンスを処理
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
        既存サーバーのヘルスチェック
        
        Returns:
            bool: サーバーが正常に応答する場合True
        """
        try:
            # 簡単なテストリクエストを送信
            test_request = ExistingServerRequest(
                model="test",
                messages=[{"role": "user", "content": "health check"}],
                stream=False
            )
            
            response = requests.post(
                self.server_url,
                json=test_request.to_dict(),
                timeout=5,  # ヘルスチェックは短いタイムアウト
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
        サーバー情報を取得
        
        Returns:
            Dict[str, Any]: サーバー情報
        """
        return {
            "server_url": self.server_url,
            "timeout": self.timeout,
            "health": self.health_check()
        }