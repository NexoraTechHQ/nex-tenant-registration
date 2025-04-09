import pytest
from unittest.mock import patch
from app.services.tenant_service import TenantService

class TestApiRoutes:
    @patch('app.routes.api.TenantService')
    def test_create_tenant_config_success(self, mock_service, client):
        """Test successful tenant creation via API."""
        mock_service.return_value.create_tenant_configuration.return_value = {
            "status": "success",
            "tenant_id": "test1234"
        }
        
        response = client.post(
            '/api/v1/tenants',
            json={'name': 'Test Tenant'}
        )
        
        assert response.status_code == 201
        assert response.json["tenant_id"] == "test1234"

    def test_create_tenant_config_invalid_input(self, client):
        """Test invalid input validation."""
        # Missing name field
        response = client.post(
            '/api/v1/tenants',
            json={'wrong_field': 'Test Tenant'}
        )
        assert response.status_code == 400
        
        # Invalid name type
        response = client.post(
            '/api/v1/tenants',
            json={'name': 123}
        )
        assert response.status_code == 400

    @patch('app.routes.api.TenantService')
    def test_create_tenant_config_failure(self, mock_service, client):
        """Test failed tenant creation via API."""
        mock_service.return_value.create_tenant_configuration.return_value = None
        
        response = client.post(
            '/api/v1/tenants',
            json={'name': 'Test Tenant'}
        )
        
        assert response.status_code == 400
        assert response.json["status"] == "error"