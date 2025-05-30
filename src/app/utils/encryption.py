"""
Encryption utilities for API keys
"""
import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


# Generate a key for encryption (in production, this should be from environment)
def get_encryption_key() -> bytes:
    """Get or generate encryption key"""
    # In production, this should come from environment variables
    password = b"your-secret-key-here"  # Replace with actual secret
    salt = b"salt_1234567890"  # Replace with actual salt
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key


def encrypt_api_key(api_key: str) -> str:
    """Encrypt an API key"""
    key = get_encryption_key()
    f = Fernet(key)
    encrypted = f.encrypt(api_key.encode())
    return base64.urlsafe_b64encode(encrypted).decode()


def decrypt_api_key(encrypted_key: str) -> str:
    """Decrypt an API key"""
    key = get_encryption_key()
    f = Fernet(key)
    encrypted_bytes = base64.urlsafe_b64decode(encrypted_key.encode())
    decrypted = f.decrypt(encrypted_bytes)
    return decrypted.decode()


# Aliases for generic encryption functions
def encrypt_data(data: str) -> str:
    """Encrypt arbitrary data"""
    return encrypt_api_key(data)


def decrypt_data(encrypted_data: str) -> str:
    """Decrypt arbitrary data"""
    return decrypt_api_key(encrypted_data)
