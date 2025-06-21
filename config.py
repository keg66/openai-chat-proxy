"""
Configuration management module
Loads settings from environment variables and provides default values
"""
import os
from typing import Optional


class Config:
    """Application configuration"""
    
    @staticmethod
    def EXISTING_SERVER_URL() -> str:
        return os.getenv("EXISTING_SERVER_URL", "http://localhost:3000/chat")
    
    @staticmethod
    def REQUEST_TIMEOUT() -> int:
        return int(os.getenv("REQUEST_TIMEOUT", "30"))
    
    @staticmethod
    def HOST() -> str:
        return os.getenv("HOST", "localhost")
    
    @staticmethod
    def PORT() -> int:
        return int(os.getenv("PORT", "8000"))
    
    @staticmethod
    def DEBUG() -> bool:
        debug_value = os.getenv("DEBUG", "false").lower()
        return debug_value in ("true", "1", "yes", "on")
    
    @staticmethod
    def LOG_LEVEL() -> str:
        return os.getenv("LOG_LEVEL", "INFO")
    
    @staticmethod
    def DEFAULT_MODEL() -> str:
        return os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo")
    
    @classmethod
    def validate(cls) -> None:
        """Validate configuration"""
        if not cls.EXISTING_SERVER_URL():
            raise ValueError("EXISTING_SERVER_URL is required")
        
        if cls.REQUEST_TIMEOUT() <= 0:
            raise ValueError("REQUEST_TIMEOUT must be positive")
        
        if cls.PORT() <= 0 or cls.PORT() > 65535:
            raise ValueError("PORT must be between 1 and 65535")
    
    @classmethod
    def get_config_dict(cls) -> dict:
        """Get configuration as dictionary"""
        return {
            "existing_server_url": cls.EXISTING_SERVER_URL(),
            "request_timeout": cls.REQUEST_TIMEOUT(),
            "host": cls.HOST(),
            "port": cls.PORT(),
            "debug": cls.DEBUG(),
            "log_level": cls.LOG_LEVEL(),
            "default_model": cls.DEFAULT_MODEL()
        }