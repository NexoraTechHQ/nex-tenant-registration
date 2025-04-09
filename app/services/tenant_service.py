from typing import Dict, Optional
from ..services.pocketbase_service import PocketBaseService
from ..utils.helpers import generate_random_string

class TenantService:
    def __init__(self):
        self.pb = PocketBaseService()
    
    def generate_unique_tenant_id(self, length=8, max_attempts=10) -> Optional[str]:
        """Generate a unique tenant_id"""
        for _ in range(max_attempts):
            tenant_id = generate_random_string(length)
            if not self.pb.tenant_id_exists(tenant_id):
                return tenant_id
        return None
    
    def create_tenant_configuration(self, tenant_name: str) -> Optional[Dict]:
        """Create a complete tenant configuration"""
        # Generate unique tenant_id
        tenant_id = self.generate_unique_tenant_id()
        if not tenant_id:
            return None
        
        # Create tenant record
        tenant_data = {
            "name": tenant_name,
            "tenant_id": tenant_id
        }
        tenant_record = self.pb.create_tenant(tenant_data)
        if not tenant_record:
            return None
        
        # Load schema template
        with open('pb_schema.json', 'r') as f:
            schema = json.load(f)
        
        # Create collections
        id_mapping = {}
        prefix = f"prefix_{tenant_id}_"
        
        # First pass - create collections with non-relation fields
        for collection in schema:
            # Implementation similar to your original code
            pass
        
        # Second pass - update collections with relation fields
        for collection in schema:
            # Implementation similar to your original code
            pass
        
        return {
            "tenant_id": tenant_id,
            "tenant_name": tenant_name,
            "collections_created": len(id_mapping),
            "status": "success"
        }