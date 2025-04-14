from flask import Blueprint, request, jsonify
from ..services.tenant_service import TenantService
from ..utils.decorators import validate_json

api_blueprint = Blueprint('api', __name__)


@api_blueprint.route('/tenants', methods=['POST'])
@validate_json({'name': str})
def create_tenant_config():
    data = request.get_json()
    tenant_name = data['name']

    service = TenantService()
    result = service.create_tenant_configuration(tenant_name)

    if not result:
        return jsonify({
            "status": "error",
            "message": "Failed to create tenant configuration"
        }), 400

    return jsonify(result), 201


@api_blueprint.route('/tenants/<tenant_id>', methods=['GET'])
def get_tenant_config(tenant_id):
    # Implementation for getting tenant config
    pass
