import httpx
from ..config import Config
from ..utils.helpers import generate_random_string
from typing import Optional, Dict

class PocketBaseService:
    def __init__(self):
        self.base_url = Config.POCKETBASE_URL
        self.admin_email = Config.POCKETBASE_ADMIN_EMAIL
        self.admin_password = Config.POCKETBASE_ADMIN_PASSWORD
        self.client = httpx.Client(verify=False)
        self.token = None
        
    def authenticate(self):
        """Authenticate with PocketBase admin credentials"""
        try:
            response = self.client.post(
                f"{self.base_url}/api/admins/auth-with-password",
                json={
                    "identity": self.admin_email,
                    "password": self.admin_password
                }
            )
            response.raise_for_status()
            self.token = response.json().get('token')
            return True
        except Exception as e:
            print(f"Authentication failed: {e}")
            return False
    
    def create_collection(self, collection_data: Dict) -> Optional[Dict]:
        """Create a new collection in PocketBase"""
        if not self.token and not self.authenticate():
            return None
            
        try:
            headers = {"Authorization": self.token}
            response = self.client.post(
                f"{self.base_url}/api/collections",
                json=collection_data,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error creating collection: {e}")
            return None
    
    def update_collection(self, collection_id: str, update_data: Dict) -> Optional[Dict]:
        """Update an existing collection"""
        if not self.token and not self.authenticate():
            return None
            
        try:
            headers = {"Authorization": self.token}
            response = self.client.patch(
                f"{self.base_url}/api/collections/{collection_id}",
                json=update_data,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error updating collection: {e}")
            return None
    
    def create_tenant(self, tenant_data: Dict) -> Optional[Dict]:
        """Create a new tenant record"""
        if not self.token and not self.authenticate():
            return None
            
        try:
            headers = {"Authorization": self.token}
            response = self.client.post(
                f"{self.base_url}/api/collections/vms_tenants/records",
                json=tenant_data,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error creating tenant: {e}")
            return None
    
    def tenant_id_exists(self, tenant_id: str) -> bool:
        """Check if a tenant_id already exists"""
        try:
            response = self.client.get(
                f"{self.base_url}/api/collections/vms_tenants/records",
                params={"filter": f"tenant_id='{tenant_id}'"}
            )
            response.raise_for_status()
            return len(response.json().get('items', [])) > 0
        except Exception:
            return False