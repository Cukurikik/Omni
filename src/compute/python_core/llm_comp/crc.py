import zlib

class CompilerChecksum:
    def compute_crc32(self, data: bytes) -> int:
        if not data:
            return 0
        return zlib.crc32(data) & 0xFFFFFFFF
