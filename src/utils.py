import hashlib
import re

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_hash, password):
    return stored_hash == hashlib.sha256(password.encode()).hexdigest()

def validate_email(email):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None

def validate_package_id(package_id):
    pattern = r"^[A-Z0-9-]{6,20}$"
    return re.match(pattern, package_id) is not None

def validate_coordinates(lat, lon):
    return -90 <= lat <= 90 and -180 <= lon <= 180
