import hashlib
import re

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_hash, password):
    return stored_hash == hashlib.sha256(password.encode()).hexdigest()

def validate_package_id(package_id):
    pattern = r"^[A-Z0-9-]{6,20}$"
    return re.match(pattern, package_id) is not None
