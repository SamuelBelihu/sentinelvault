import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os

def get_key(master_password, salt):
    """Derives a cryptographic key from the Master Password and Salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    return base64.urlsafe_b64encode(kdf.derive(master_password.encode()))

def encrypt_data(plain_text, key):
    """Turns plain text into an encrypted string."""
    f = Fernet(key)
    return f.encrypt(plain_text.encode()).decode()

def decrypt_data(encrypted_text, key):
    """Turns encrypted string back into plain text."""
    f = Fernet(key)
    return f.decrypt(encrypted_text.encode()).decode()
def generate_vault_key():
    """Generates a random 32-byte key and returns it as a Fernet-compatible string."""
    return base64.urlsafe_b64encode(os.urandom(32))