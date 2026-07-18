"""
Core Service: Secure Storage.

Provides a unified interface for storing and retrieving secrets securely using the OS credential manager.
Wraps the `keyring` library to provide Windows Credential Manager / macOS Keychain integration.
"""
import keyring
import keyring.errors
from typing import Optional

SERVICE_NAME = "tellme_ai_assistant"

def set_secret(provider_id: str, key: str, secret: str):
    """
    Store a secret securely in the OS keychain.
    """
    keyring.set_password(SERVICE_NAME, f"{provider_id}_{key}", secret)

def get_secret(provider_id: str, key: str) -> Optional[str]:
    """
    Retrieve a secret from the OS keychain.
    Returns None if not found.
    """
    return keyring.get_password(SERVICE_NAME, f"{provider_id}_{key}")

def delete_secret(provider_id: str, key: str):
    """
    Delete a secret from the OS keychain.
    """
    try:
        keyring.delete_password(SERVICE_NAME, f"{provider_id}_{key}")
    except keyring.errors.PasswordDeleteError:
        pass
