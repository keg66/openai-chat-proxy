"""
設定管理のテスト
"""
import pytest
import os
from unittest.mock import patch
from config import Config


class TestConfig:
    """Configクラスのテスト"""
    
    def test_default_values(self):
        """デフォルト値のテスト"""
        # 環境変数をクリア
        with patch.dict(os.environ, {}, clear=True):
            assert Config.EXISTING_SERVER_URL() == "http://localhost:3000/chat"
            assert Config.REQUEST_TIMEOUT() == 30
            assert Config.HOST() == "localhost"
            assert Config.PORT() == 8000
            assert Config.DEBUG() is False
            assert Config.LOG_LEVEL() == "INFO"
            assert Config.DEFAULT_MODEL() == "gpt-3.5-turbo"
    
    def test_environment_variable_override(self):
        """環境変数による設定上書きのテスト"""
        env_vars = {
            "EXISTING_SERVER_URL": "http://custom-server.com/api",
            "REQUEST_TIMEOUT": "60",
            "HOST": "0.0.0.0",
            "PORT": "9000",
            "DEBUG": "true",
            "LOG_LEVEL": "DEBUG",
            "DEFAULT_MODEL": "gpt-4"
        }
        
        with patch.dict(os.environ, env_vars):
            assert Config.EXISTING_SERVER_URL() == "http://custom-server.com/api"
            assert Config.REQUEST_TIMEOUT() == 60
            assert Config.HOST() == "0.0.0.0"
            assert Config.PORT() == 9000
            assert Config.DEBUG() is True
            assert Config.LOG_LEVEL() == "DEBUG"
            assert Config.DEFAULT_MODEL() == "gpt-4"
    
    def test_debug_false_values(self):
        """DEBUG環境変数のfalse値のテスト"""
        false_values = ["false", "False", "FALSE", "0", "no", "off"]
        
        for false_value in false_values:
            with patch.dict(os.environ, {"DEBUG": false_value}):
                assert Config.DEBUG() is False
    
    def test_debug_true_values(self):
        """DEBUG環境変数のtrue値のテスト"""
        true_values = ["true", "True", "TRUE", "1", "yes", "on"]
        
        for true_value in true_values:
            with patch.dict(os.environ, {"DEBUG": true_value}):
                assert Config.DEBUG() is True
    
    def test_validate_success(self):
        """設定検証成功のテスト"""
        with patch.dict(os.environ, {
            "EXISTING_SERVER_URL": "http://valid-server.com",
            "REQUEST_TIMEOUT": "30",
            "PORT": "8000"
        }):
            # 例外が発生しないことを確認
            Config.validate()
    
    def test_validate_empty_server_url(self):
        """空のサーバーURL検証エラーのテスト"""
        with patch.dict(os.environ, {"EXISTING_SERVER_URL": ""}):
            with pytest.raises(ValueError, match="EXISTING_SERVER_URL is required"):
                Config.validate()
    
    def test_validate_invalid_timeout(self):
        """無効なタイムアウト値検証エラーのテスト"""
        with patch.dict(os.environ, {"REQUEST_TIMEOUT": "0"}):
            with pytest.raises(ValueError, match="REQUEST_TIMEOUT must be positive"):
                Config.validate()
        
        with patch.dict(os.environ, {"REQUEST_TIMEOUT": "-1"}):
            with pytest.raises(ValueError, match="REQUEST_TIMEOUT must be positive"):
                Config.validate()
    
    def test_validate_invalid_port(self):
        """無効なポート番号検証エラーのテスト"""
        with patch.dict(os.environ, {"PORT": "0"}):
            with pytest.raises(ValueError, match="PORT must be between 1 and 65535"):
                Config.validate()
        
        with patch.dict(os.environ, {"PORT": "65536"}):
            with pytest.raises(ValueError, match="PORT must be between 1 and 65535"):
                Config.validate()
        
        with patch.dict(os.environ, {"PORT": "-1"}):
            with pytest.raises(ValueError, match="PORT must be between 1 and 65535"):
                Config.validate()
    
    def test_get_config_dict(self):
        """設定辞書取得のテスト"""
        with patch.dict(os.environ, {
            "EXISTING_SERVER_URL": "http://test.com",
            "REQUEST_TIMEOUT": "45",
            "HOST": "127.0.0.1",
            "PORT": "8080",
            "DEBUG": "true",
            "LOG_LEVEL": "WARNING",
            "DEFAULT_MODEL": "gpt-4"
        }):
            config_dict = Config.get_config_dict()
            
            expected = {
                "existing_server_url": "http://test.com",
                "request_timeout": 45,
                "host": "127.0.0.1",
                "port": 8080,
                "debug": True,
                "log_level": "WARNING",
                "default_model": "gpt-4"
            }
            
            assert config_dict == expected
    
    def test_type_conversion(self):
        """型変換のテスト"""
        with patch.dict(os.environ, {
            "REQUEST_TIMEOUT": "123",
            "PORT": "9999"
        }):
            assert isinstance(Config.REQUEST_TIMEOUT(), int)
            assert isinstance(Config.PORT(), int)
            assert Config.REQUEST_TIMEOUT() == 123
            assert Config.PORT() == 9999