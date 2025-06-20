"""
アダプター設定管理
既存サーバーとの互換性のための設定を管理
"""
import os
import json
import logging
from typing import Dict, Any, Optional


class AdapterConfig:
    """アダプター設定クラス"""
    
    @staticmethod
    def ADAPTER_TYPE() -> str:
        return os.getenv("ADAPTER_TYPE", "openai_compatible")
    
    @staticmethod
    def REQUEST_MODEL_FIELD() -> str:
        return os.getenv("REQUEST_MODEL_FIELD", "model")
    
    @staticmethod
    def REQUEST_MESSAGES_FIELD() -> str:
        return os.getenv("REQUEST_MESSAGES_FIELD", "messages")
    
    @staticmethod
    def REQUEST_TEMPERATURE_FIELD() -> str:
        return os.getenv("REQUEST_TEMPERATURE_FIELD", "temperature")
    
    @staticmethod
    def REQUEST_MAX_TOKENS_FIELD() -> str:
        return os.getenv("REQUEST_MAX_TOKENS_FIELD", "max_tokens")
    
    @staticmethod
    def REQUEST_STREAM_FIELD() -> str:
        return os.getenv("REQUEST_STREAM_FIELD", "stream")
    
    @staticmethod
    def REQUEST_STOP_FIELD() -> str:
        return os.getenv("REQUEST_STOP_FIELD", "stop")
    
    @staticmethod
    def RESPONSE_CONTENT_FIELD() -> str:
        return os.getenv("RESPONSE_CONTENT_FIELD", "content")
    
    @staticmethod
    def RESPONSE_FINISH_FIELD() -> str:
        return os.getenv("RESPONSE_FINISH_FIELD", "finish_reason")
    
    @staticmethod
    def RESPONSE_MODEL_FIELD() -> str:
        return os.getenv("RESPONSE_MODEL_FIELD", "model")
    
    @staticmethod
    def RESPONSE_CREATED_FIELD() -> str:
        return os.getenv("RESPONSE_CREATED_FIELD", "created")
    
    @staticmethod
    def STREAMING_FORMAT() -> str:
        return os.getenv("STREAMING_FORMAT", "sse")
    
    @staticmethod
    def STREAMING_DATA_PREFIX() -> str:
        return os.getenv("STREAMING_DATA_PREFIX", "data: ")
    
    @staticmethod
    def STREAMING_DONE_MARKER() -> str:
        return os.getenv("STREAMING_DONE_MARKER", "[DONE]")
    
    @staticmethod
    def CUSTOM_HEADERS() -> Dict[str, str]:
        try:
            return json.loads(os.getenv("CUSTOM_HEADERS", "{}"))
        except json.JSONDecodeError:
            return {}
    
    @staticmethod
    def REQUEST_TRANSFORM() -> str:
        return os.getenv("REQUEST_TRANSFORM", "none")
    
    @staticmethod
    def RESPONSE_TRANSFORM() -> str:
        return os.getenv("RESPONSE_TRANSFORM", "none")
    
    @staticmethod
    def ADAPTER_DEBUG() -> bool:
        return os.getenv("ADAPTER_DEBUG", "false").lower() == "true"
    
    @classmethod
    def validate(cls) -> None:
        """設定の妥当性をチェック"""
        logger = logging.getLogger(__name__)
        
        # 必須フィールドのチェック
        if not cls.REQUEST_MESSAGES_FIELD():
            raise ValueError("REQUEST_MESSAGES_FIELD is required")
        
        if not cls.RESPONSE_CONTENT_FIELD():
            raise ValueError("RESPONSE_CONTENT_FIELD is required")
        
        # ストリーミング設定の整合性チェック
        if cls.STREAMING_FORMAT() not in ["sse", "jsonlines", "none"]:
            raise ValueError(f"Invalid STREAMING_FORMAT: {cls.STREAMING_FORMAT()}")
        
        if cls.STREAMING_FORMAT() != "none" and not cls.REQUEST_STREAM_FIELD():
            logger.warning("Streaming format specified but REQUEST_STREAM_FIELD is empty")
        
        # カスタムヘッダーの検証
        try:
            custom_headers_str = os.getenv("CUSTOM_HEADERS", "{}")
            json.loads(custom_headers_str)
        except json.JSONDecodeError:
            raise ValueError("CUSTOM_HEADERS must be a valid JSON object")
        
        logger.info("Adapter configuration validated successfully")
    
    @classmethod
    def get_adapter_info(cls) -> Dict[str, Any]:
        """アダプター設定情報を取得"""
        return {
            "adapter_type": cls.ADAPTER_TYPE(),
            "request_mapping": {
                "model": cls.REQUEST_MODEL_FIELD() or None,
                "messages": cls.REQUEST_MESSAGES_FIELD(),
                "temperature": cls.REQUEST_TEMPERATURE_FIELD() or None,
                "max_tokens": cls.REQUEST_MAX_TOKENS_FIELD() or None,
                "stream": cls.REQUEST_STREAM_FIELD() or None,
                "stop": cls.REQUEST_STOP_FIELD() or None,
            },
            "response_mapping": {
                "content": cls.RESPONSE_CONTENT_FIELD(),
                "finish_reason": cls.RESPONSE_FINISH_FIELD() or None,
                "model": cls.RESPONSE_MODEL_FIELD() or None,
                "created": cls.RESPONSE_CREATED_FIELD() or None,
            },
            "streaming": {
                "format": cls.STREAMING_FORMAT(),
                "data_prefix": cls.STREAMING_DATA_PREFIX(),
                "done_marker": cls.STREAMING_DONE_MARKER(),
            },
            "transforms": {
                "request": cls.REQUEST_TRANSFORM(),
                "response": cls.RESPONSE_TRANSFORM(),
            },
            "custom_headers": cls.CUSTOM_HEADERS(),
            "debug": cls.ADAPTER_DEBUG()
        }
    
    @classmethod
    def log_configuration(cls) -> None:
        """使用中のアダプター設定をログ出力"""
        logger = logging.getLogger(__name__)
        
        logger.info("=== Adapter Configuration ===")
        logger.info(f"Adapter Type: {cls.ADAPTER_TYPE()}")
        
        logger.info("Request Field Mapping:")
        logger.info(f"  messages → {cls.REQUEST_MESSAGES_FIELD()}")
        
        if cls.REQUEST_MODEL_FIELD():
            logger.info(f"  model → {cls.REQUEST_MODEL_FIELD()}")
        else:
            logger.info("  model field: DISABLED")
        
        if cls.REQUEST_TEMPERATURE_FIELD():
            logger.info(f"  temperature → {cls.REQUEST_TEMPERATURE_FIELD()}")
        else:
            logger.info("  temperature field: DISABLED")
        
        if cls.REQUEST_MAX_TOKENS_FIELD():
            logger.info(f"  max_tokens → {cls.REQUEST_MAX_TOKENS_FIELD()}")
        else:
            logger.info("  max_tokens field: DISABLED")
        
        if cls.REQUEST_STREAM_FIELD():
            logger.info(f"  stream → {cls.REQUEST_STREAM_FIELD()}")
        else:
            logger.info("  stream field: DISABLED")
        
        logger.info("Response Field Mapping:")
        logger.info(f"  content ← {cls.RESPONSE_CONTENT_FIELD()}")
        
        if cls.RESPONSE_FINISH_FIELD():
            logger.info(f"  finish_reason ← {cls.RESPONSE_FINISH_FIELD()}")
        else:
            logger.info("  finish_reason field: DISABLED (will use 'stop')")
        
        if cls.RESPONSE_MODEL_FIELD():
            logger.info(f"  model ← {cls.RESPONSE_MODEL_FIELD()}")
        else:
            logger.info("  model field: DISABLED")
        
        logger.info(f"Streaming: {cls.STREAMING_FORMAT()}")
        if cls.STREAMING_FORMAT() != "none":
            logger.info(f"  Data prefix: '{cls.STREAMING_DATA_PREFIX()}'")
            logger.info(f"  Done marker: '{cls.STREAMING_DONE_MARKER()}'")
        
        custom_headers = cls.CUSTOM_HEADERS()
        if custom_headers:
            logger.info(f"Custom Headers: {len(custom_headers)} header(s)")
            for key in custom_headers.keys():
                logger.info(f"  {key}: [REDACTED]")
        else:
            logger.info("Custom Headers: None")
        
        logger.info("==============================")


def get_nested_value(data: Dict[str, Any], field_path: str) -> Any:
    """
    ネストしたフィールドパスから値を取得
    
    Args:
        data: データ辞書
        field_path: フィールドパス（例: "response.choices[0].message.content"）
    
    Returns:
        取得した値、存在しない場合はNone
    """
    if not field_path or not data:
        return None
    
    try:
        keys = field_path.split('.')
        value = data
        
        for key in keys:
            # 配列インデックスの処理 (例: choices[0])
            if '[' in key and ']' in key:
                field_name = key[:key.index('[')]
                index = int(key[key.index('[') + 1:key.index(']')])
                value = value[field_name][index]
            else:
                value = value[key]
        
        return value
    except (KeyError, TypeError, IndexError, ValueError):
        return None


def set_nested_value(data: Dict[str, Any], field_path: str, value: Any) -> None:
    """
    ネストしたフィールドパスに値を設定
    
    Args:
        data: データ辞書
        field_path: フィールドパス
        value: 設定する値
    """
    if not field_path:
        return
    
    keys = field_path.split('.')
    current = data
    
    # 最後のキーまでの階層を作成
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    
    # 最後のキーに値を設定
    last_key = keys[-1]
    current[last_key] = value