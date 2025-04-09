import pytest
from unittest.mock import patch, MagicMock
from app.services.pocketbase_service import PocketBaseService

class TestPocketBaseService:
    @patch('httpx.Client')
    def test_authenticate_success(self, mock_client):
        """Test successful authentication."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"token": "test-token"}
        mock_client.return_value.post.return_value = mock_response

        pb = PocketBaseService()
        assert pb.authenticate() is True
        assert pb.token == "test-token"

    @patch('httpx.Client')
    def test_authenticate_failure(self, mock_client):
        """Test failed authentication."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_client.return_value.post.return_value = mock_response

        pb = PocketBaseService()
        assert pb.authenticate() is False
        assert pb.token is None

    @patch('httpx.Client')
    def test_create_collection_success(self, mock_client):
        """Test successful collection creation."""
        mock_auth_response = MagicMock()
        mock_auth_response.status_code = 200
        mock_auth_response.json.return_value = {"token": "test-token"}
        
        mock_create_response = MagicMock()
        mock_create_response.status_code = 200
        mock_create_response.json.return_value = {"id": "col123", "name": "test"}
        
        mock_client.return_value.post.side_effect = [mock_auth_response, mock_create_response]

        pb = PocketBaseService()
        result = pb.create_collection({"name": "test"})
        assert result == {"id": "col123", "name": "test"}

    @patch('httpx.Client')
    def test_tenant_id_exists(self, mock_client):
        """Test tenant ID existence check."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": [{"tenant_id": "exists123"}]}
        mock_client.return_value.get.return_value = mock_response

        pb = PocketBaseService()
        assert pb.tenant_id_exists("exists123") is True
        assert pb.tenant_id_exists("nonexistent") is False