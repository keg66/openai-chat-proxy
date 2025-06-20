"""
ベースアダプタークラス
異なる既存サーバーとの互換性を提供するための基底クラス
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Generator, Optional
import logging

from ..models import ChatCompletionRequest, ExistingServerRequest, ExistingServerResponse


class BaseAdapter(ABC):
    """アダプターのベースクラス"""
    
    def __init__(self, config):
        """
        Args:
            config: アダプター設定オブジェクト
        """
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        if config.ADAPTER_DEBUG:
            self.logger.setLevel(logging.DEBUG)
    
    @abstractmethod
    def transform_request(self, openai_request: ChatCompletionRequest) -> Dict[str, Any]:
        """
        OpenAI形式のリクエストを既存サーバー形式に変換
        
        Args:
            openai_request: OpenAI形式のリクエスト
            
        Returns:
            Dict: 既存サーバー用のリクエストデータ
        """
        pass
    
    @abstractmethod
    def transform_response(self, server_response: Dict[str, Any], original_request: ChatCompletionRequest) -> ExistingServerResponse:
        """
        既存サーバーのレスポンスをプロキシ用形式に変換
        
        Args:
            server_response: 既存サーバーからのレスポンス
            original_request: 元のOpenAIリクエスト
            
        Returns:
            ExistingServerResponse: プロキシ用レスポンス
        """
        pass
    
    @abstractmethod
    def parse_streaming_chunk(self, chunk_line: str) -> Optional[Dict[str, Any]]:
        """
        ストリーミングレスポンスのチャンクを解析
        
        Args:
            chunk_line: ストリーミングデータの1行
            
        Returns:
            Dict: 解析されたチャンクデータ、解析できない場合はNone
        """
        pass
    
    @abstractmethod
    def get_custom_headers(self) -> Dict[str, str]:
        """
        カスタムヘッダーを取得
        
        Returns:
            Dict: カスタムヘッダー辞書
        """
        pass
    
    def log_request_transform(self, openai_request: ChatCompletionRequest, transformed_request: Dict[str, Any]) -> None:
        """リクエスト変換をログ出力（デバッグ用）"""
        if self.config.ADAPTER_DEBUG:
            self.logger.debug("Request transformation:")
            self.logger.debug(f"  Original: model={openai_request.model}, messages_count={len(openai_request.messages)}, stream={openai_request.stream}")
            self.logger.debug(f"  Transformed: {transformed_request}")
    
    def log_response_transform(self, server_response: Dict[str, Any], transformed_response: ExistingServerResponse) -> None:
        """レスポンス変換をログ出力（デバッグ用）"""
        if self.config.ADAPTER_DEBUG:
            self.logger.debug("Response transformation:")
            self.logger.debug(f"  Server response keys: {list(server_response.keys())}")
            self.logger.debug(f"  Transformed: content_length={len(transformed_response.content)}, finish_reason={transformed_response.finish_reason}")


class AdapterError(Exception):
    """アダプター関連のエラー"""
    pass


class UnsupportedFormatError(AdapterError):
    """サポートされていない形式エラー"""
    pass


class MappingError(AdapterError):
    """フィールドマッピングエラー"""
    pass