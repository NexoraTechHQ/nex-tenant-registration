import random
import string

def generate_random_string(length=8) -> str:
    """Generate a random alphanumeric string"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def validate_tenant_name(name: str) -> bool:
    """Validate tenant name meets requirements"""
    return len(name) >= 3 and name.isalnum()