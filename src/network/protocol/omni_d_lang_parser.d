module omni.binary_parser;

// Omni Binary Protocol Parser (D Language)
// Compute & Network Layer
// Uses D's powerful compile-time execution (CTFE) and system-level features
// to parse highly compressed binary payloads for inference data streams.

import core.stdc.string : memcpy;

struct OmniHeader {
    uint magic;
    ushort version_;
    ushort payloadType;
    ulong payloadLength;
}

enum OMNI_MAGIC_BYTES = 0x4F4D4E49; // "OMNI"

class BinaryStreamParser {
    
    // Parses a raw byte buffer and extracts the header and tensor payload
    static bool parse(const(ubyte)[] buffer, out OmniHeader header, out const(ubyte)[] payload) {
        if (buffer.length < OmniHeader.sizeof) {
            return false; // Buffer too small
        }

        // Direct memory cast (zero copy parsing)
        header = *(cast(const(OmniHeader)*) buffer.ptr);

        if (header.magic != OMNI_MAGIC_BYTES) {
            return false; // Invalid magic number
        }
        
        if (buffer.length < OmniHeader.sizeof + header.payloadLength) {
            return false; // Incomplete payload
        }

        // Slice out the payload (zero copy)
        payload = buffer[OmniHeader.sizeof .. OmniHeader.sizeof + header.payloadLength];
        
        return true;
    }
}
