"""
アダプターファクトリー
設定に基づいて適切なアダプターを生成
"""
import logging
from typing import Dict, Type
from .base import BaseAdapter
from .configurable import ConfigurableAdapter
from ..adapter_config import AdapterConfig


class AdapterFactory:
    """アダプターファクトリークラス"""
    
    # 利用可能なアダプター
    _adapters: Dict[str, Type[BaseAdapter]] = {
        "openai_compatible": ConfigurableAdapter,
        "configurable": ConfigurableAdapter,
        "mock_server": ConfigurableAdapter,
        "custom": ConfigurableAdapter,  # 将来的にカスタムアダプター用
    }
    
    @classmethod
    def create_adapter(cls, config: AdapterConfig = None) -> BaseAdapter:
        """
        設定に基づいてアダプターを作成
        
        Args:
            config: アダプター設定（Noneの場合はデフォルト設定を使用）
            
        Returns:
            BaseAdapter: 作成されたアダプター
            
        Raises:
            ValueError: 不明なアダプタータイプの場合
        """
        if config is None:
            config = AdapterConfig
        
        adapter_type = config.ADAPTER_TYPE().lower()
        
        if adapter_type not in cls._adapters:
            raise ValueError(f"Unknown adapter type: {adapter_type}. Available types: {list(cls._adapters.keys())}")
        
        adapter_class = cls._adapters[adapter_type]
        adapter = adapter_class(config)
        
        logger = logging.getLogger(__name__)
        logger.info(f"Created adapter: {adapter_class.__name__} (type: {adapter_type})")
        
        return adapter
    
    @classmethod
    def register_adapter(cls, adapter_type: str, adapter_class: Type[BaseAdapter]) -> None:
        """
        新しいアダプターを登録
        
        Args:
            adapter_type: アダプタータイプ名
            adapter_class: アダプタークラス
        """
        cls._adapters[adapter_type.lower()] = adapter_class
        
        logger = logging.getLogger(__name__)
        logger.info(f"Registered new adapter: {adapter_class.__name__} (type: {adapter_type})")
    
    @classmethod
    def get_available_adapters(cls) -> Dict[str, Type[BaseAdapter]]:
        """
        利用可能なアダプターの一覧を取得
        
        Returns:
            Dict: アダプタータイプとクラスの辞書
        """
        return cls._adapters.copy()
    
    @classmethod
    def validate_adapter_config(cls, config: AdapterConfig) -> bool:
        """
        アダプター設定の妥当性を検証
        
        Args:
            config: 検証するアダプター設定
            
        Returns:
            bool: 設定が有効な場合True
        """
        try:
            # 設定の基本検証
            config.validate()
            
            # アダプタータイプの存在確認
            if config.ADAPTER_TYPE().lower() not in cls._adapters:
                return False
            
            # アダプターの作成テスト
            adapter = cls.create_adapter(config)
            
            logger = logging.getLogger(__name__)
            logger.info(f"Adapter configuration validation passed for type: {config.ADAPTER_TYPE()}")
            
            return True
            
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Adapter configuration validation failed: {e}")
            return False


def get_default_adapter() -> BaseAdapter:
    """
    デフォルトアダプターを取得
    
    Returns:
        BaseAdapter: デフォルト設定で作成されたアダプター
    """
    return AdapterFactory.create_adapter()