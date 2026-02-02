"""
Security Service Module
Provides encryption and decryption functionality using Python standard library
"""
import base64
import hashlib
import json
import os
from typing import Any, Dict


class SecurityService:
    """Handles encryption and decryption of sensitive data"""
    
    def __init__(self, key: str = None):
        """
        Initialize SecurityService with encryption key
        
        Args:
            key: Encryption key (if None, generates from machine-specific data)
        """
        if key is None:
            # Generate key from machine-specific information
            key = self._generate_machine_key()
        
        # Create encryption key from password
        self._key = self._derive_key(key)
    
    def _generate_machine_key(self) -> str:
        """
        Generate a machine-specific encryption key
        
        Returns:
            Machine-specific key string
        """
        # Use machine name and user name to create a unique key
        import platform
        machine_id = f"{platform.node()}-{os.getlogin()}-PasteGuardian"
        return machine_id
    
    def _derive_key(self, password: str) -> bytes:
        """
        Derive encryption key from password using PBKDF2
        
        Args:
            password: Password string
            
        Returns:
            32-byte encryption key
        """
        # Use SHA256 to create a consistent 32-byte key
        return hashlib.sha256(password.encode()).digest()
    
    def encrypt_string(self, plaintext: str) -> str:
        """
        Encrypt a string using XOR cipher with key
        
        Args:
            plaintext: String to encrypt
            
        Returns:
            Base64-encoded encrypted string
        """
        if not plaintext:
            return ""
        
        # Convert to bytes
        plaintext_bytes = plaintext.encode('utf-8')
        
        # XOR encryption
        encrypted_bytes = bytearray()
        key_length = len(self._key)
        
        for i, byte in enumerate(plaintext_bytes):
            encrypted_bytes.append(byte ^ self._key[i % key_length])
        
        # Encode to base64 for safe storage
        return base64.b64encode(bytes(encrypted_bytes)).decode('utf-8')
    
    def decrypt_string(self, ciphertext: str) -> str:
        """
        Decrypt a string encrypted with encrypt_string
        
        Args:
            ciphertext: Base64-encoded encrypted string
            
        Returns:
            Decrypted plaintext string
        """
        if not ciphertext:
            return ""
        
        try:
            # Decode from base64
            encrypted_bytes = base64.b64decode(ciphertext.encode('utf-8'))
            
            # XOR decryption (same as encryption for XOR)
            decrypted_bytes = bytearray()
            key_length = len(self._key)
            
            for i, byte in enumerate(encrypted_bytes):
                decrypted_bytes.append(byte ^ self._key[i % key_length])
            
            return bytes(decrypted_bytes).decode('utf-8')
        except Exception as e:
            print(f"Decryption error: {e}")
            return ""
    
    def encrypt_dict(self, data: Dict[str, Any], fields_to_encrypt: list = None) -> Dict[str, Any]:
        """
        Encrypt specific fields in a dictionary
        
        Args:
            data: Dictionary to encrypt
            fields_to_encrypt: List of field names to encrypt (None = all string fields)
            
        Returns:
            Dictionary with encrypted fields
        """
        encrypted_data = data.copy()
        
        if fields_to_encrypt is None:
            # Encrypt all string fields
            fields_to_encrypt = [k for k, v in data.items() if isinstance(v, str)]
        
        for field in fields_to_encrypt:
            if field in encrypted_data and isinstance(encrypted_data[field], str):
                encrypted_data[field] = self.encrypt_string(encrypted_data[field])
                encrypted_data[f"__{field}_encrypted__"] = True
        
        return encrypted_data
    
    def decrypt_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decrypt fields in a dictionary that were encrypted with encrypt_dict
        
        Args:
            data: Dictionary with encrypted fields
            
        Returns:
            Dictionary with decrypted fields
        """
        decrypted_data = data.copy()
        
        # Find encrypted fields by looking for encryption markers
        encrypted_fields = []
        for key in list(data.keys()):
            if key.startswith("__") and key.endswith("_encrypted__"):
                # Extract field name: __password_encrypted__ -> password
                # Remove __ prefix (2 chars) and _encrypted__ suffix (12 chars)
                field_name = key[2:-12]
                encrypted_fields.append(field_name)
        
        for field in encrypted_fields:
            if field in decrypted_data:
                # Decrypt the field
                decrypted_data[field] = self.decrypt_string(decrypted_data[field])
                # Remove encryption marker
                marker_key = f"__{field}_encrypted__"
                if marker_key in decrypted_data:
                    del decrypted_data[marker_key]
        
        return decrypted_data
    
    def hash_data(self, data: str) -> str:
        """
        Create a hash of data (for integrity checking)
        
        Args:
            data: Data to hash
            
        Returns:
            Hex string of hash
        """
        return hashlib.sha256(data.encode()).hexdigest()
    
    def verify_hash(self, data: str, hash_value: str) -> bool:
        """
        Verify data against hash
        
        Args:
            data: Data to verify
            hash_value: Expected hash value
            
        Returns:
            True if hash matches, False otherwise
        """
        return self.hash_data(data) == hash_value


# Global instance
security_service = SecurityService()


def encrypt_sensitive_data(data: str) -> str:
    """
    Convenience function to encrypt sensitive data
    
    Args:
        data: Sensitive data to encrypt
        
    Returns:
        Encrypted string
    """
    return security_service.encrypt_string(data)


def decrypt_sensitive_data(encrypted_data: str) -> str:
    """
    Convenience function to decrypt sensitive data
    
    Args:
        encrypted_data: Encrypted data
        
    Returns:
        Decrypted string
    """
    return security_service.decrypt_string(encrypted_data)
