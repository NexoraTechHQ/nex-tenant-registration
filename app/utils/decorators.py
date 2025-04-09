from functools import wraps
from flask import request, jsonify

def validate_json(expected_fields):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not request.is_json:
                return jsonify({"error": "Request must be JSON"}), 400
            
            data = request.get_json()
            for field, field_type in expected_fields.items():
                if field not in data:
                    return jsonify({"error": f"Missing field: {field}"}), 400
                if not isinstance(data[field], field_type):
                    return jsonify({"error": f"Invalid type for {field}"}), 400
            
            return f(*args, **kwargs)
        return wrapped
    return decorator