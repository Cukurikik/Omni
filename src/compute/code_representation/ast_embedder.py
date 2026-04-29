import ctypes

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class ASTEmbedder:
    def __init__(self):
        self.lib = ctypes.CDLL('./system/code_representation/tree_sitter_ffi.so')
        self.lib.omni_parse_ast_hash.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_int)]
        self.lib.omni_parse_ast_hash.restype = ctypes.c_double

    def embed_code(self, source_code: str) -> OmniResult:
        if not source_code:
            return OmniResult(error="Source code cannot be empty")

        err_code = ctypes.c_int(0)
        source_bytes = source_code.encode('utf-8')
        ast_hash = self.lib.omni_parse_ast_hash(source_bytes, ctypes.byref(err_code))

        if err_code.value != 0:
            return OmniResult(error=f"AST parsing failed with code {err_code.value}")

        return OmniResult(value={'ast_hash': ast_hash})

def generate_code_embedding(code: str) -> OmniResult:
    embedder = ASTEmbedder()
    return embedder.embed_code(code)
