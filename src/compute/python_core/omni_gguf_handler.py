"""
OMNI Compute — GGML Tensor Format Handler
Read/write GGUF model files for quantized inference.
"""
import struct, logging, os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, BinaryIO
from pathlib import Path

logger = logging.getLogger("omni.ggml")

GGUF_MAGIC = 0x46475547  # "GGUF"
GGUF_VERSION = 3

class GGMLType:
    F32 = 0; F16 = 1; Q4_0 = 2; Q4_1 = 3; Q5_0 = 6; Q5_1 = 7; Q8_0 = 8; Q8_1 = 9
    Q2_K = 10; Q3_K = 11; Q4_K = 12; Q5_K = 13; Q6_K = 14
    NAMES = {0:"F32",1:"F16",2:"Q4_0",3:"Q4_1",6:"Q5_0",7:"Q5_1",8:"Q8_0",9:"Q8_1",
             10:"Q2_K",11:"Q3_K",12:"Q4_K",13:"Q5_K",14:"Q6_K"}
    BYTES_PER_ELEMENT = {0:4, 1:2, 2:0.5625, 3:0.625, 6:0.6875, 7:0.75, 8:1.0625,
                         9:1.125, 10:0.3125, 11:0.4375, 12:0.5625, 13:0.6875, 14:0.8125}

@dataclass
class GGUFTensorInfo:
    name: str; ndim: int; shape: List[int]; dtype: int; offset: int
    @property
    def numel(self) -> int: return 1 if not self.shape else 1
    @property
    def type_name(self) -> str: return GGMLType.NAMES.get(self.dtype, f"UNK({self.dtype})")
    @property
    def size_bytes(self) -> int:
        n = 1
        for s in self.shape: n *= s
        return int(n * GGMLType.BYTES_PER_ELEMENT.get(self.dtype, 4))

@dataclass
class GGUFHeader:
    magic: int = GGUF_MAGIC; version: int = GGUF_VERSION
    num_tensors: int = 0; num_kv: int = 0
    metadata: Dict = field(default_factory=dict)
    tensors: List[GGUFTensorInfo] = field(default_factory=list)

class OmniGGUFReader:
    """Read and parse GGUF model files."""
    def __init__(self, path: str):
        self.path = Path(path); self.header = GGUFHeader()
        self._file: Optional[BinaryIO] = None
    def _read_u32(self) -> int: return struct.unpack('<I', self._file.read(4))[0]
    def _read_u64(self) -> int: return struct.unpack('<Q', self._file.read(8))[0]
    def _read_i32(self) -> int: return struct.unpack('<i', self._file.read(4))[0]
    def _read_string(self) -> str:
        length = self._read_u64()
        return self._file.read(length).decode('utf-8')
    def read_header(self) -> GGUFHeader:
        self._file = open(self.path, 'rb')
        magic = self._read_u32()
        if magic != GGUF_MAGIC: raise ValueError(f"Invalid GGUF magic: {hex(magic)}")
        version = self._read_u32()
        num_tensors = self._read_u64()
        num_kv = self._read_u64()
        self.header = GGUFHeader(magic=magic, version=version,
                                  num_tensors=num_tensors, num_kv=num_kv)
        logger.info(f"GGUF v{version}: {num_tensors} tensors, {num_kv} metadata entries")
        return self.header
    def get_model_info(self) -> Dict:
        file_size = os.path.getsize(self.path)
        return {"path": str(self.path), "file_size_mb": file_size / (1024*1024),
                "version": self.header.version, "num_tensors": self.header.num_tensors,
                "num_metadata": self.header.num_kv}
    def close(self):
        if self._file: self._file.close()

class OmniGGUFWriter:
    """Write GGUF model files."""
    def __init__(self, path: str):
        self.path = Path(path); self.metadata: Dict = {}
        self.tensors: List[GGUFTensorInfo] = []
    def add_metadata(self, key: str, value):
        self.metadata[key] = value
    def add_tensor(self, name: str, shape: List[int], dtype: int, data: bytes):
        info = GGUFTensorInfo(name=name, ndim=len(shape), shape=shape,
                               dtype=dtype, offset=0)
        self.tensors.append((info, data))
    def write(self):
        with open(self.path, 'wb') as f:
            f.write(struct.pack('<I', GGUF_MAGIC))
            f.write(struct.pack('<I', GGUF_VERSION))
            f.write(struct.pack('<Q', len(self.tensors)))
            f.write(struct.pack('<Q', len(self.metadata)))
            logger.info(f"Written GGUF header: {len(self.tensors)} tensors")
