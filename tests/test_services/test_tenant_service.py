import pytest
from unittest.mock import patch, MagicMock
from app.services.tenant_service import TenantService

class TestTenantService:
    @patch('app.services.tenant_service.PocketBaseService')
    def test_generate_unique_tenant_id(self, mock_pb):
        """Test generating unique tenant ID."""
        mock_pb.return_value.tenant_id_exists.side_effect = [True, True, False]
        
        service = TenantService()
        tenant_id = service.generate_unique_tenant_id()
        assert len(tenant_id) == 8
        assert mock_pb.return_value.tenant_id_exists.call_count == 3

    @patch('app.services.tenant_service.PocketBaseService')
    @patch('builtins.open')
    @patch('json.load')
    def test_create_tenant_configuration_success(self, mock_json, mock_open, mock_pb):
        """Test successful tenant configuration creation."""
        # Setup mocks
        mock_pb_instance = mock_pb.return_value
        mock_pb_instance.generate_unique_tenant_id.return_value = "test1234"
        mock_pb_instance.create_tenant.return_value = {"id": "rec123", "tenant_id": "test1234"}
        mock_pb_instance.create_collection.return_value = {"id": "col123"}
        mock_pb_instance.update_collection.return_value = {"id": "col123"}
        
        mock_json.return_value = [{
            "id": "col1",
            "name": "test_collection",
            "schema": []
        }]
        
        service = TenantService()
        result = service.create_tenant_configuration("Test Tenant")
        
        assert result["status"] == "success"
        assert result["tenant_id"] == "test1234"
        assert result["collections_created"] == 1

    @patch('app.services.tenant_service.PocketBaseService')
    def test_create_tenant_configuration_failure(self, mock_pb):
        """Test failed tenant configuration creation."""
        mock_pb_instance = mock_pb.return_value
        mock_pb_instance.generate_unique_tenant_id.return_value = None
        
        service = TenantService()
        result = service.create_tenant_configuration("Test Tenant")
        assert result is None