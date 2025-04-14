import json
import os
from typing import Dict, List, Optional
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

    def clean_field(self, field: Dict) -> Dict:
        """Remove unsupported field properties for the PocketBase client."""
        supported_keys = ["name", "type", "required",
                          "presentable", "unique", "options"]
        if field["type"] == "autodate":
            field["type"] = "date"  # Convert autodate to date
        return {key: field[key] for key in supported_keys if key in field}

    def is_relation_field(self, field: Dict) -> bool:
        """Check if a field is a relation field."""
        return field["type"] == "relation" and "options" in field and "collectionId" in field["options"]

    def get_non_relation_fields(self, collection: Dict) -> List[Dict]:
        """Extract non-relation fields from a collection schema."""
        if "schema" not in collection:
            return []

        return [
            self.clean_field(field)
            for field in collection["schema"]
            if not self.is_relation_field(field)
        ]

    def get_relation_fields(self, collection: Dict) -> List[Dict]:
        """Extract relation fields from a collection schema."""
        if "schema" not in collection:
            return []

        return [
            self.clean_field(field)
            for field in collection["schema"]
            if self.is_relation_field(field)
        ]

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

        # Calculate path to pb_schema.json
        current_dir = os.path.dirname(
            os.path.abspath(__file__))  # Get services directory
        app_dir = os.path.dirname(current_dir)  # Navigate up to app directory
        schema_path = os.path.join(
            app_dir, 'schema-collection', 'v1', 'pb_schema.json')

        try:
            # Load schema template
            with open(schema_path, 'r') as f:
                schema = json.load(f)

            # Dictionary to store original ID to new ID mapping
            id_mapping = {}
            app_prefix = "vms"  # Using 'vms' as the app prefix based on your example

            # First pass - create all collections with non-relation fields
            for collection in schema:
                original_name = collection["name"]
                base_name = original_name.split('_')[-1]
                collection_name = f"{app_prefix}_{tenant_id}_{base_name}"
                # Get non-relation fields
                non_relation_fields = self.get_non_relation_fields(collection)

                # If no non-relation fields exist, add a dummy field
                if not non_relation_fields and "schema" in collection:
                    non_relation_fields = [{
                        "name": "dummy_field",
                        "type": "text",
                        "required": False,
                        "options": {}
                    }]
                    print(
                        f"Added dummy field to {collection_name} for initial creation")

                # Create the collection with non-relation fields
                collection_data = {
                    "name": collection_name,
                    "type": collection["type"],
                    "schema": non_relation_fields,
                    "listRule": collection.get("listRule"),
                    "viewRule": collection.get("viewRule"),
                    "createRule": collection.get("createRule"),
                    "updateRule": collection.get("updateRule"),
                    "deleteRule": collection.get("deleteRule"),
                    "options": collection.get("options", {})
                }

                try:
                    created_collection = self.pb.create_collection(
                        collection_data)
                    print(f"{collection_name} created successfully!")
                    id_mapping[collection["id"]] = created_collection["id"]
                except Exception as e:
                    print(f"Error creating {collection_name}: {e}")
                    continue

            # Second pass - update collections to add relation fields
            for collection in schema:
                original_name = collection["name"]
                collection_id = id_mapping.get(collection["id"])
                base_name = original_name.split('_')[-1]
                collection_name = f"{app_prefix}_{tenant_id}_{base_name}"

                if not collection_id:
                    print(
                        f"Skipping {collection_name} - not created in first pass")
                    continue

                # Get all fields including relations (with updated collection IDs)
                all_fields = []
                if "schema" in collection:
                    for field in collection["schema"]:
                        cleaned_field = self.clean_field(field)

                        # Handle relation fields
                        if self.is_relation_field(field):
                            original_related_id = field["options"]["collectionId"]
                            if original_related_id in id_mapping:
                                cleaned_field["options"] = {
                                    "collectionId": id_mapping[original_related_id],
                                    "cascadeDelete": field["options"].get("cascadeDelete", False),
                                    "minSelect": field["options"].get("minSelect"),
                                    "maxSelect": field["options"].get("maxSelect"),
                                    "displayFields": field["options"].get("displayFields")
                                }

                        all_fields.append(cleaned_field)

                # For collections that had a dummy field, remove it now
                if any(f["name"] == "dummy_field" for f in all_fields):
                    all_fields = [
                        f for f in all_fields if f["name"] != "dummy_field"]
                    print(f"Removed dummy field from {collection_name}")

                # Update the collection with all fields
                try:
                    update_data = {"schema": all_fields}
                    self.pb.update_collection(collection_id, update_data)
                    print(
                        f"Updated {collection_name} with all fields and relations")
                except Exception as e:
                    print(f"Error updating {collection_name}: {e}")

            return {
                "tenant_id": tenant_id,
                "tenant_name": tenant_name,
                "collections_created": len(id_mapping),
                "status": "success"
            }

        except FileNotFoundError:
            print(f"Schema file not found at {schema_path}")
            return None
        except json.JSONDecodeError:
            print(f"Invalid JSON in schema file at {schema_path}")
            return None
        except Exception as e:
            print(f"Unexpected error during tenant configuration: {e}")
            return None
