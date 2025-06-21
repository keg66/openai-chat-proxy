"""
Tests for Models API functionality
"""
import pytest
import json
import os
import tempfile
from unittest.mock import patch, MagicMock

from app_flask import app
from config import Config
from core.models import Model, ModelsResponse
from core.client import ExistingServerClient
from core.converter import DataConverter


class TestModelsAPI:
    """Test Models API endpoint"""
    
    def setup_method(self):
        """Setup for each test"""
        self.app = app.test_client()
        self.app.testing = True
    
    def test_models_endpoint_with_existing_server(self):
        """Test models endpoint when existing server has models API"""
        mock_server_response = {
            "models": [
                {"id": "server-model-1", "name": "Server Model 1"},
                {"id": "server-model-2", "name": "Server Model 2"}
            ]
        }
        
        with patch.object(Config, 'EXISTING_SERVER_MODELS_URL', return_value="http://test.com/models"):
            with patch.object(ExistingServerClient, 'get_models', return_value=mock_server_response):
                response = self.app.get('/v1/models')
                
                assert response.status_code == 200
                data = response.get_json()
                
                assert data["object"] == "list"
                assert len(data["data"]) == 2
                assert data["data"][0]["id"] == "server-model-1"
                assert data["data"][1]["id"] == "server-model-2"
    
    def test_models_endpoint_with_config_file(self):
        """Test models endpoint loading from config file"""
        config_data = {
            "object": "list",
            "data": [
                {
                    "id": "config-model-1",
                    "object": "model",
                    "created": 1677610602,
                    "owned_by": "test",
                    "permission": [],
                    "root": "config-model-1",
                    "parent": None
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_file = f.name
        
        try:
            with patch.object(Config, 'EXISTING_SERVER_MODELS_URL', return_value=""):
                with patch.object(Config, 'MODELS_CONFIG_FILE', return_value=temp_file):
                    response = self.app.get('/v1/models')
                    
                    assert response.status_code == 200
                    data = response.get_json()
                    
                    assert data["object"] == "list"
                    assert len(data["data"]) == 1
                    assert data["data"][0]["id"] == "config-model-1"
                    assert data["data"][0]["owned_by"] == "test"
        finally:
            os.unlink(temp_file)
    
    def test_models_endpoint_with_default_model(self):
        """Test models endpoint with default model when config file not found"""
        with patch.object(Config, 'EXISTING_SERVER_MODELS_URL', return_value=""):
            with patch.object(Config, 'MODELS_CONFIG_FILE', return_value="nonexistent.json"):
                with patch.object(Config, 'DEFAULT_MODEL', return_value="default-model"):
                    response = self.app.get('/v1/models')
                    
                    assert response.status_code == 200
                    data = response.get_json()
                    
                    assert data["object"] == "list"
                    assert len(data["data"]) == 1
                    assert data["data"][0]["id"] == "default-model"
                    assert data["data"][0]["owned_by"] == "default"
    
    def test_models_endpoint_server_error_with_fallback(self):
        """Test models endpoint when server fails but fallback is enabled"""
        config_data = {
            "object": "list",
            "data": [
                {
                    "id": "fallback-model",
                    "object": "model",
                    "created": 1677610602,
                    "owned_by": "fallback",
                    "permission": [],
                    "root": "fallback-model",
                    "parent": None
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_file = f.name
        
        try:
            with patch.object(Config, 'EXISTING_SERVER_MODELS_URL', return_value="http://test.com/models"):
                with patch.object(Config, 'MODELS_FALLBACK_ENABLED', return_value=True):
                    with patch.object(Config, 'MODELS_CONFIG_FILE', return_value=temp_file):
                        with patch.object(ExistingServerClient, 'get_models', side_effect=Exception("Server error")):
                            response = self.app.get('/v1/models')
                            
                            assert response.status_code == 200
                            data = response.get_json()
                            
                            assert data["object"] == "list"
                            assert len(data["data"]) == 1
                            assert data["data"][0]["id"] == "fallback-model"
        finally:
            os.unlink(temp_file)
    
    def test_models_endpoint_server_error_no_fallback(self):
        """Test models endpoint when server fails and fallback is disabled"""
        with patch.object(Config, 'EXISTING_SERVER_MODELS_URL', return_value="http://test.com/models"):
            with patch.object(Config, 'MODELS_FALLBACK_ENABLED', return_value=False):
                with patch.object(ExistingServerClient, 'get_models', side_effect=Exception("Server error")):
                    response = self.app.get('/v1/models')
                    
                    assert response.status_code == 503
                    data = response.get_json()
                    
                    assert "error" in data
                    assert "Failed to get models from existing server" in data["error"]["message"]


class TestModelDataStructures:
    """Test Model and ModelsResponse data structures"""
    
    def test_model_creation(self):
        """Test Model creation and conversion"""
        model = Model(
            id="test-model",
            owned_by="test-owner"
        )
        
        assert model.id == "test-model"
        assert model.object == "model"
        assert model.owned_by == "test-owner"
        assert model.root == "test-model"  # Should default to id
        assert model.parent is None
        assert isinstance(model.created, int)
        assert isinstance(model.permission, list)
    
    def test_model_from_dict(self):
        """Test Model creation from dictionary"""
        data = {
            "id": "dict-model",
            "object": "model",
            "created": 1677610602,
            "owned_by": "dict-owner",
            "permission": [{"test": "permission"}],
            "root": "dict-root",
            "parent": "dict-parent"
        }
        
        model = Model.from_dict(data)
        
        assert model.id == "dict-model"
        assert model.created == 1677610602
        assert model.owned_by == "dict-owner"
        assert model.permission == [{"test": "permission"}]
        assert model.root == "dict-root"
        assert model.parent == "dict-parent"
    
    def test_model_to_dict(self):
        """Test Model conversion to dictionary"""
        model = Model(
            id="to-dict-model",
            owned_by="to-dict-owner"
        )
        
        result = model.to_dict()
        
        assert result["id"] == "to-dict-model"
        assert result["object"] == "model"
        assert result["owned_by"] == "to-dict-owner"
        assert result["root"] == "to-dict-model"
        assert result["parent"] is None
        assert isinstance(result["created"], int)
        assert isinstance(result["permission"], list)
    
    def test_models_response_creation(self):
        """Test ModelsResponse creation"""
        models = [
            Model(id="model-1", owned_by="owner-1"),
            Model(id="model-2", owned_by="owner-2")
        ]
        
        response = ModelsResponse(data=models)
        
        assert response.object == "list"
        assert len(response.data) == 2
        assert response.data[0].id == "model-1"
        assert response.data[1].id == "model-2"
    
    def test_models_response_from_dict(self):
        """Test ModelsResponse creation from dictionary"""
        data = {
            "object": "list",
            "data": [
                {"id": "dict-model-1", "owned_by": "dict-owner-1"},
                {"id": "dict-model-2", "owned_by": "dict-owner-2"}
            ]
        }
        
        response = ModelsResponse.from_dict(data)
        
        assert response.object == "list"
        assert len(response.data) == 2
        assert response.data[0].id == "dict-model-1"
        assert response.data[1].id == "dict-model-2"
    
    def test_models_response_to_dict(self):
        """Test ModelsResponse conversion to dictionary"""
        models = [
            Model(id="to-dict-model-1", owned_by="to-dict-owner-1"),
            Model(id="to-dict-model-2", owned_by="to-dict-owner-2")
        ]
        
        response = ModelsResponse(data=models)
        result = response.to_dict()
        
        assert result["object"] == "list"
        assert len(result["data"]) == 2
        assert result["data"][0]["id"] == "to-dict-model-1"
        assert result["data"][1]["id"] == "to-dict-model-2"


class TestModelsClientMethods:
    """Test client methods for models API"""
    
    def setup_method(self):
        """Setup for each test"""
        self.client = ExistingServerClient("http://test.com")
    
    @patch('requests.get')
    def test_get_models_success(self, mock_get):
        """Test successful models API call"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": [{"id": "test-model"}]}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.client.get_models("http://test.com/models")
        
        assert result == {"models": [{"id": "test-model"}]}
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_get_models_connection_error(self, mock_get):
        """Test models API connection error"""
        from requests.exceptions import ConnectionError
        mock_get.side_effect = ConnectionError("Connection failed")
        
        with pytest.raises(ConnectionError):
            self.client.get_models("http://test.com/models")
    
    @patch('requests.get')
    def test_get_models_timeout(self, mock_get):
        """Test models API timeout"""
        from requests.exceptions import Timeout
        mock_get.side_effect = Timeout("Request timeout")
        
        with pytest.raises(Timeout):
            self.client.get_models("http://test.com/models")


class TestModelsAdapterTransformation:
    """Test adapter transformation for models"""
    
    def setup_method(self):
        """Setup for each test"""
        from core.adapters.factory import get_default_adapter
        self.adapter = get_default_adapter()
        self.converter = DataConverter(self.adapter)
    
    def test_transform_models_response(self):
        """Test models response transformation through adapter"""
        server_response = {
            "models": [
                {"id": "server-model-1", "name": "Server Model 1"},
                {"id": "server-model-2", "name": "Server Model 2"}
            ]
        }
        
        result = self.converter.transform_models_response(server_response)
        
        assert isinstance(result, ModelsResponse)
        assert result.object == "list"
        assert len(result.data) == 2
        assert result.data[0].id == "server-model-1"
        assert result.data[1].id == "server-model-2"
    
    def test_transform_models_empty_response(self):
        """Test models transformation with empty response"""
        server_response = {"models": []}
        
        result = self.converter.transform_models_response(server_response)
        
        assert isinstance(result, ModelsResponse)
        assert result.object == "list"
        assert len(result.data) == 0
    
    def test_transform_models_invalid_response(self):
        """Test models transformation with invalid response"""
        server_response = {"invalid": "data"}
        
        result = self.converter.transform_models_response(server_response)
        
        assert isinstance(result, ModelsResponse)
        assert result.object == "list"
        assert len(result.data) == 0