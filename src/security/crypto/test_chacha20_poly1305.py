"""Tests for ChaCha20-Poly1305 AEAD implementation"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.security.crypto.chacha20_poly1305_aead import ChaCha20Poly1305, CryptoError
import pytest


class TestChaCha20Poly1305KeyValidation:
    def test_generate_key_returns_32_bytes(self):
        key = ChaCha20Poly1305.generate_key()
        assert len(key) == 32

    def test_generate_key_is_random(self):
        key1 = ChaCha20Poly1305.generate_key()
        key2 = ChaCha20Poly1305.generate_key()
        assert key1 != key2

    def test_init_valid_key(self):
        key = ChaCha20Poly1305.generate_key()
        cipher = ChaCha20Poly1305(key)
        assert cipher is not None

    def test_init_short_key_raises(self):
        with pytest.raises(CryptoError, match="Key must be exactly 32 bytes"):
            ChaCha20Poly1305(b"short_key")

    def test_init_long_key_raises(self):
        with pytest.raises(CryptoError, match="Key must be exactly 32 bytes"):
            ChaCha20Poly1305(b"a" * 33)


class TestChaCha20Poly1305NonceValidation:
    def setup_method(self):
        self.key = ChaCha20Poly1305.generate_key()
        self.cipher = ChaCha20Poly1305(self.key)

    def test_generate_nonce_returns_12_bytes(self):
        nonce = ChaCha20Poly1305.generate_nonce()
        assert len(nonce) == 12

    def test_generate_nonce_is_random(self):
        nonce1 = ChaCha20Poly1305.generate_nonce()
        nonce2 = ChaCha20Poly1305.generate_nonce()
        assert nonce1 != nonce2

    def test_encrypt_short_nonce_raises(self):
        with pytest.raises(CryptoError, match="Nonce must be exactly 12 bytes"):
            self.cipher.encrypt(b"test", b"short")

    def test_decrypt_short_nonce_raises(self):
        with pytest.raises(CryptoError, match="Nonce must be exactly 12 bytes"):
            self.cipher.decrypt(b"test", b"short")


class TestChaCha20Poly1305Encryption:
    def setup_method(self):
        self.key = ChaCha20Poly1305.generate_key()
        self.cipher = ChaCha20Poly1305(self.key)
        self.nonce = ChaCha20Poly1305.generate_nonce()

    def test_encrypt_decrypt_roundtrip(self):
        plaintext = b"Hello, OMNI Security!"
        encrypted = self.cipher.encrypt(plaintext, self.nonce)
        decrypted = self.cipher.decrypt(encrypted, self.nonce)
        assert decrypted == plaintext

    def test_encrypt_empty_plaintext_raises(self):
        with pytest.raises(CryptoError, match="Plaintext cannot be empty"):
            self.cipher.encrypt(b"", self.nonce)

    def test_encrypt_produces_different_ciphertext_with_different_nonce(self):
        plaintext = b"Secret message"
        nonce1 = ChaCha20Poly1305.generate_nonce()
        nonce2 = ChaCha20Poly1305.generate_nonce()
        ct1 = self.cipher.encrypt(plaintext, nonce1)
        ct2 = self.cipher.encrypt(plaintext, nonce2)
        assert ct1 != ct2

    def test_encrypt_includes_mac_tag(self):
        plaintext = b"Test data"
        encrypted = self.cipher.encrypt(plaintext, self.nonce)
        # Ciphertext + 16-byte MAC tag
        assert len(encrypted) == len(plaintext) + 16

    def test_decrypt_with_associated_data(self):
        plaintext = b"Authenticated data test"
        ad = b"header:version=1"
        encrypted = self.cipher.encrypt(plaintext, self.nonce, associated_data=ad)
        decrypted = self.cipher.decrypt(encrypted, self.nonce, associated_data=ad)
        assert decrypted == plaintext

    def test_decrypt_wrong_associated_data_raises(self):
        plaintext = b"Authenticated data test"
        encrypted = self.cipher.encrypt(plaintext, self.nonce, associated_data=b"correct_ad")
        with pytest.raises(CryptoError, match="MAC Verification Failed"):
            self.cipher.decrypt(encrypted, self.nonce, associated_data=b"wrong_ad")


class TestChaCha20Poly1305TamperDetection:
    def setup_method(self):
        self.key = ChaCha20Poly1305.generate_key()
        self.cipher = ChaCha20Poly1305(self.key)
        self.nonce = ChaCha20Poly1305.generate_nonce()

    def test_tampered_ciphertext_raises(self):
        plaintext = b"Sensitive data"
        encrypted = self.cipher.encrypt(plaintext, self.nonce)
        # Flip a byte
        tampered = bytes([encrypted[0] ^ 0xFF]) + encrypted[1:]
        with pytest.raises(CryptoError, match="MAC Verification Failed"):
            self.cipher.decrypt(tampered, self.nonce)

    def test_tampered_tag_raises(self):
        plaintext = b"Sensitive data"
        encrypted = self.cipher.encrypt(plaintext, self.nonce)
        # Flip last byte of tag
        tampered = encrypted[:-1] + bytes([encrypted[-1] ^ 0xFF])
        with pytest.raises(CryptoError, match="MAC Verification Failed"):
            self.cipher.decrypt(tampered, self.nonce)

    def test_wrong_key_raises(self):
        plaintext = b"Sensitive data"
        encrypted = self.cipher.encrypt(plaintext, self.nonce)
        wrong_cipher = ChaCha20Poly1305(ChaCha20Poly1305.generate_key())
        with pytest.raises(CryptoError, match="MAC Verification Failed"):
            wrong_cipher.decrypt(encrypted, self.nonce)

    def test_wrong_nonce_raises(self):
        plaintext = b"Sensitive data"
        encrypted = self.cipher.encrypt(plaintext, self.nonce)
        wrong_nonce = ChaCha20Poly1305.generate_nonce()
        with pytest.raises(CryptoError, match="MAC Verification Failed"):
            self.cipher.decrypt(encrypted, wrong_nonce)

    def test_truncated_payload_raises(self):
        with pytest.raises(CryptoError, match="Payload too small"):
            self.cipher.decrypt(b"short", self.nonce)


class TestChaCha20Poly1305LargeData:
    def setup_method(self):
        self.key = ChaCha20Poly1305.generate_key()
        self.cipher = ChaCha20Poly1305(self.key)
        self.nonce = ChaCha20Poly1305.generate_nonce()

    def test_encrypt_decrypt_large_payload(self):
        # 1MB payload
        large_data = os.urandom(1024 * 1024)
        encrypted = self.cipher.encrypt(large_data, self.nonce)
        decrypted = self.cipher.decrypt(encrypted, self.nonce)
        assert decrypted == large_data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
