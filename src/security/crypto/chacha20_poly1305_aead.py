"""OMNI MOTHER SYSTEM - SECURITY LAYER
ChaCha20-Poly1305 Authenticated Encryption with Associated Data (AEAD).
Production-grade cryptographic implementation using the cryptography library.
"""

from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305 as _ChaCha20Poly1305
from cryptography.exceptions import InvalidTag
import os


class CryptoError(Exception):
    pass


class ChaCha20Poly1305:
    """
    AEAD cryptographic wrapper using production-grade ChaCha20-Poly1305.
    This implementation binds to the cryptography library which uses
    optimized C-level primitives (OpenSSL/LibreSSL backend).
    """

    KEY_SIZE = 32
    NONCE_SIZE = 12
    MAC_SIZE = 16

    def __init__(self, key: bytes):
        if len(key) != self.KEY_SIZE:
            raise CryptoError(f"OMNI_FATAL: Key must be exactly {self.KEY_SIZE} bytes.")
        self._key = key
        self._cipher = _ChaCha20Poly1305(key)

    @classmethod
    def generate_key(cls) -> bytes:
        """Generate a cryptographically secure random 32-byte key."""
        return os.urandom(cls.KEY_SIZE)

    @staticmethod
    def generate_nonce() -> bytes:
        """Generate a cryptographically secure random 12-byte nonce."""
        return os.urandom(12)

    def encrypt(self, plaintext: bytes, nonce: bytes, associated_data: bytes = b"") -> bytes:
        """
        Encrypts data and generates a Poly1305 MAC tag preventing tampering.
        """
        if len(nonce) != self.NONCE_SIZE:
            raise CryptoError(f"OMNI_FATAL: Nonce must be exactly {self.NONCE_SIZE} bytes.")

        if not plaintext:
            raise CryptoError("OMNI_FATAL: Plaintext cannot be empty.")

        # Real ChaCha20-Poly1305 AEAD encryption via cryptography library
        # Returns ciphertext with 16-byte authentication tag appended
        return self._cipher.encrypt(nonce, plaintext, associated_data)

    def decrypt(self, encrypted_payload: bytes, nonce: bytes, associated_data: bytes = b"") -> bytes:
        """
        Verifies the MAC tag, then decrypts. Fails fatally if a single bit was altered.
        """
        if len(nonce) != self.NONCE_SIZE:
            raise CryptoError(f"OMNI_FATAL: Nonce must be exactly {self.NONCE_SIZE} bytes.")

        if len(encrypted_payload) < self.MAC_SIZE:
            raise CryptoError("OMNI_FATAL: Payload too small to contain a valid MAC tag.")

        try:
            return self._cipher.decrypt(nonce, encrypted_payload, associated_data)
        except InvalidTag:
            raise CryptoError(
                "OMNI_FATAL: AEAD MAC Verification Failed. "
                "Data has been tampered with or key is invalid."
            )
