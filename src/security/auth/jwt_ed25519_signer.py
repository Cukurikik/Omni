"""OMNI MOTHER SYSTEM - SECURITY LAYER
JWT Ed25519 Signer & Validator.
Production-grade implementation using the cryptography library.
Enforces strong asymmetric signatures over weak symmetric HMACs.
"""

import json
import base64
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
    PrivateFormat,
    NoEncryption,
)
from cryptography.exceptions import InvalidSignature


class JwtSecurityError(Exception):
    pass


class JwtEd25519Provider:
    """
    Constructs and verifies JSON Web Tokens utilizing Edwards-curve Digital
    Signature Algorithm (EdDSA) via Ed25519.

    This implementation binds to the `cryptography` library which uses
    optimized C-level primitives.
    """

    def __init__(self, private_key_bytes: bytes = None, public_key_bytes: bytes = None):
        self._private_key: Ed25519PrivateKey | None = None
        self._public_key: Ed25519PublicKey | None = None

        if private_key_bytes:
            if len(private_key_bytes) == 64:
                # Raw 64-byte expanded private key
                self._private_key = Ed25519PrivateKey.from_private_bytes(private_key_bytes[:32])
            elif len(private_key_bytes) == 32:
                # Raw 32-byte seed
                self._private_key = Ed25519PrivateKey.from_private_bytes(private_key_bytes)
            else:
                # Try DER/PEM loading
                try:
                    from cryptography.hazmat.primitives.serialization import (
                        load_pem_private_key,
                        load_der_private_key,
                    )
                    if private_key_bytes.startswith(b"-----BEGIN"):
                        self._private_key = load_pem_private_key(private_key_bytes, password=None)
                    else:
                        self._private_key = load_der_private_key(private_key_bytes, password=None)
                except Exception:
                    raise JwtSecurityError("OMNI_FATAL: Unable to load private key")

        if public_key_bytes:
            if len(public_key_bytes) == 32:
                self._public_key = Ed25519PublicKey.from_public_bytes(public_key_bytes)
            else:
                try:
                    from cryptography.hazmat.primitives.serialization import (
                        load_pem_public_key,
                        load_der_public_key,
                    )
                    if public_key_bytes.startswith(b"-----BEGIN"):
                        self._public_key = load_pem_public_key(public_key_bytes)
                    else:
                        self._public_key = load_der_public_key(public_key_bytes)
                except Exception:
                    raise JwtSecurityError("OMNI_FATAL: Unable to load public key")

    @classmethod
    def generate_keys(cls) -> tuple[bytes, bytes]:
        """Generate a new Ed25519 keypair. Returns (private_key_raw, public_key_raw)."""
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        # Use serialization for compatibility
        priv_raw = private_key.private_bytes(
            Encoding.Raw, PrivateFormat.Raw, NoEncryption()
        )
        pub_raw = public_key.public_bytes(Encoding.Raw, PublicFormat.Raw)
        return priv_raw, pub_raw

    def sign_token(self, payload: dict) -> str:
        """
        Generates a strictly compliant EdDSA JWT.
        """
        if not self._private_key:
            raise JwtSecurityError("OMNI_FATAL: Private key missing. Cannot sign token.")

        header = {"alg": "EdDSA", "typ": "JWT"}

        # Base64Url encoding
        hdr_b64 = self._b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
        pld_b64 = self._b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))

        signing_input = f"{hdr_b64}.{pld_b64}".encode("utf-8")

        # Real Ed25519 signing via cryptography library
        signature = self._private_key.sign(signing_input)

        sig_b64 = self._b64url_encode(signature)

        return f"{hdr_b64}.{pld_b64}.{sig_b64}"

    def verify_token(self, jwt: str) -> dict:
        """
        Verifies token integrity and decodes the payload.
        """
        if not self._public_key:
            raise JwtSecurityError("OMNI_FATAL: Public key missing. Cannot verify token.")

        parts = jwt.split(".")
        if len(parts) != 3:
            raise JwtSecurityError("Malformed JWT structure.")

        signing_input = f"{parts[0]}.{parts[1]}".encode("utf-8")
        signature = self._b64url_decode(parts[2])

        if len(signature) != 64:
            raise JwtSecurityError("OMNI_FATAL: Invalid Ed25519 signature length.")

        # Real Ed25519 verification
        try:
            self._public_key.verify(signature, signing_input)
        except InvalidSignature:
            raise JwtSecurityError("OMNI_FATAL: Signature verification failed. Possible forgery.")

        # Decode payload safely
        payload_bytes = self._b64url_decode(parts[1])
        return json.loads(payload_bytes.decode("utf-8"))

    def get_public_key_pem(self) -> bytes:
        """Export public key as PEM."""
        if not self._public_key:
            raise JwtSecurityError("OMNI_FATAL: No public key available.")
        return self._public_key.public_bytes(
            Encoding.PEM, PublicFormat.SubjectPublicKeyInfo
        )

    def get_private_key_pem(self) -> bytes:
        """Export private key as PEM."""
        if not self._private_key:
            raise JwtSecurityError("OMNI_FATAL: No private key available.")
        return self._private_key.private_bytes(
            Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()
        )

    def _b64url_encode(self, data: bytes) -> str:
        return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")

    def _b64url_decode(self, b64str: str) -> bytes:
        pad = b"=" * (4 - (len(b64str) % 4))
        return base64.urlsafe_b64decode(b64str.encode("utf-8") + pad)
