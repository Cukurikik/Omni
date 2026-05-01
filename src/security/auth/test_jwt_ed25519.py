"""Tests for JWT Ed25519 Signer implementation"""

import sys
import os
import json
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.security.auth.jwt_ed25519_signer import JwtEd25519Provider, JwtSecurityError
import pytest


class TestJwtEd25519KeyGeneration:
    def test_generate_keys_returns_tuple(self):
        priv, pub = JwtEd25519Provider.generate_keys()
        assert len(priv) == 32  # Ed25519 private key seed
        assert len(pub) == 32   # Ed25519 public key

    def test_generate_keys_is_random(self):
        priv1, pub1 = JwtEd25519Provider.generate_keys()
        priv2, pub2 = JwtEd25519Provider.generate_keys()
        assert priv1 != priv2
        assert pub1 != pub2

    def test_init_with_raw_key_bytes(self):
        priv, pub = JwtEd25519Provider.generate_keys()
        provider = JwtEd25519Provider(private_key_bytes=priv, public_key_bytes=pub)
        assert provider is not None

    def test_init_without_keys(self):
        provider = JwtEd25519Provider()
        assert provider is not None


class TestJwtEd25519Signing:
    def setup_method(self):
        priv, pub = JwtEd25519Provider.generate_keys()
        self.provider = JwtEd25519Provider(private_key_bytes=priv, public_key_bytes=pub)

    def test_sign_token_returns_jwt_string(self):
        payload = {"sub": "user123", "role": "admin"}
        token = self.provider.sign_token(payload)
        assert isinstance(token, str)

    def test_sign_token_has_three_parts(self):
        payload = {"sub": "user123", "role": "admin"}
        token = self.provider.sign_token(payload)
        parts = token.split(".")
        assert len(parts) == 3

    def test_sign_token_header_is_eddsa(self):
        payload = {"sub": "user123"}
        token = self.provider.sign_token(payload)
        header_b64 = token.split(".")[0]
        # Add padding for decoding
        padded = header_b64 + "=" * (4 - len(header_b64) % 4)
        import base64
        header = json.loads(base64.urlsafe_b64decode(padded))
        assert header["alg"] == "EdDSA"
        assert header["typ"] == "JWT"

    def test_sign_token_without_private_key_raises(self):
        provider = JwtEd25519Provider()
        with pytest.raises(JwtSecurityError, match="Private key missing"):
            provider.sign_token({"sub": "user"})

    def test_sign_token_produces_unique_signatures(self):
        # Ed25519 is deterministic, so same input = same signature
        payload = {"sub": "user123", "iat": 1234567890}
        token1 = self.provider.sign_token(payload)
        token2 = self.provider.sign_token(payload)
        assert token1 == token2

    def test_sign_token_different_payloads_produce_different_tokens(self):
        token1 = self.provider.sign_token({"sub": "user1"})
        token2 = self.provider.sign_token({"sub": "user2"})
        assert token1 != token2


class TestJwtEd25519Verification:
    def setup_method(self):
        priv, pub = JwtEd25519Provider.generate_keys()
        self.provider = JwtEd25519Provider(private_key_bytes=priv, public_key_bytes=pub)

    def test_verify_token_returns_payload(self):
        payload = {"sub": "user123", "role": "admin", "iat": 1234567890}
        token = self.provider.sign_token(payload)
        verified = self.provider.verify_token(token)
        assert verified["sub"] == "user123"
        assert verified["role"] == "admin"

    def test_verify_token_without_public_key_raises(self):
        provider = JwtEd25519Provider()
        with pytest.raises(JwtSecurityError, match="Public key missing"):
            provider.verify_token("any.token.here")

    def test_verify_malformed_jwt_raises(self):
        with pytest.raises(JwtSecurityError, match="Malformed JWT structure"):
            self.provider.verify_token("only.two")

    def test_verify_tampered_payload_raises(self):
        payload = {"sub": "user123", "role": "user"}
        token = self.provider.sign_token(payload)
        parts = token.split(".")
        # Tamper with payload
        import base64
        tampered_payload = base64.urlsafe_b64encode(
            json.dumps({"sub": "user123", "role": "admin"}).encode()
        ).decode().rstrip("=")
        tampered_token = f"{parts[0]}.{tampered_payload}.{parts[2]}"
        with pytest.raises(JwtSecurityError, match="Signature verification failed|Possible forgery"):
            self.provider.verify_token(tampered_token)

    def test_verify_wrong_public_key_raises(self):
        priv1, _ = JwtEd25519Provider.generate_keys()
        _, pub2 = JwtEd25519Provider.generate_keys()
        signer = JwtEd25519Provider(private_key_bytes=priv1)
        verifier = JwtEd25519Provider(public_key_bytes=pub2)
        token = signer.sign_token({"sub": "user"})
        with pytest.raises(JwtSecurityError, match="Signature verification failed|Possible forgery"):
            verifier.verify_token(token)

    def test_verify_tampered_signature_raises(self):
        payload = {"sub": "user123"}
        token = self.provider.sign_token(payload)
        parts = token.split(".")
        # Tamper with signature heavily (replace multiple characters)
        sig = parts[2]
        # Change first 4 characters to ensure it breaks
        tampered_sig = "AAAA" + sig[4:]
        tampered_token = f"{parts[0]}.{parts[1]}.{tampered_sig}"
        with pytest.raises(JwtSecurityError):
            self.provider.verify_token(tampered_token)


class TestJwtEd25519RealWorldScenarios:
    def setup_method(self):
        priv, pub = JwtEd25519Provider.generate_keys()
        self.provider = JwtEd25519Provider(private_key_bytes=priv, public_key_bytes=pub)

    def test_jwt_with_expiry(self):
        payload = {
            "sub": "user123",
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600  # 1 hour
        }
        token = self.provider.sign_token(payload)
        verified = self.provider.verify_token(token)
        assert verified["exp"] > verified["iat"]

    def test_jwt_with_multiple_claims(self):
        payload = {
            "sub": "user123",
            "iss": "omni-auth",
            "aud": ["api", "web"],
            "roles": ["admin", "editor"],
            "permissions": ["read", "write", "delete"],
        }
        token = self.provider.sign_token(payload)
        verified = self.provider.verify_token(token)
        assert verified["iss"] == "omni-auth"
        assert "admin" in verified["roles"]

    def test_jwt_payload_with_unicode(self):
        payload = {
            "sub": "user_123",
            "name": "Juan Garc\u00eda",
            "email": "juan@example.com",
        }
        token = self.provider.sign_token(payload)
        verified = self.provider.verify_token(token)
        assert verified["name"] == "Juan Garc\u00eda"

    def test_jwt_empty_payload(self):
        payload = {}
        token = self.provider.sign_token(payload)
        verified = self.provider.verify_token(token)
        assert verified == {}

    def test_key_export_pem(self):
        priv, pub = JwtEd25519Provider.generate_keys()
        provider = JwtEd25519Provider(private_key_bytes=priv, public_key_bytes=pub)
        pub_pem = provider.get_public_key_pem()
        priv_pem = provider.get_private_key_pem()
        assert pub_pem.startswith(b"-----BEGIN PUBLIC KEY-----")
        assert priv_pem.startswith(b"-----BEGIN PRIVATE KEY-----")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
