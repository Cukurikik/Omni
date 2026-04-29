#include <stdint.h>
#include <stddef.h>

extern "C" {

// FFI export for deterministic MIDI byte stream encoding from raw notes
void omni_encode_midi_stream(
    const int32_t* note_events, // Format: [pitch, velocity, duration_ticks]
    int32_t num_events,
    uint8_t* out_buffer,
    int32_t max_buffer_size,
    int32_t* bytes_written,
    int32_t* err_code
) {
    if (!err_code) return;
    
    if (!note_events || !out_buffer || !bytes_written || num_events <= 0 || max_buffer_size < 14) {
        *err_code = -1;
        return;
    }

    int32_t offset = 0;

    // 1. Write MIDI Header Chunk (MThd)
    const uint8_t header[] = {
        0x4D, 0x54, 0x68, 0x64, // "MThd"
        0x00, 0x00, 0x00, 0x06, // Chunk size
        0x00, 0x00,             // Format 0 (single track)
        0x00, 0x01,             // 1 track
        0x00, 0x60              // 96 ticks per quarter note
    };

    for (int i = 0; i < 14; ++i) out_buffer[offset++] = header[i];

    // 2. Track Chunk Header (MTrk)
    // We will leave the size blank and fill it later
    const uint8_t track_header[] = { 0x4D, 0x54, 0x72, 0x6B }; // "MTrk"
    for (int i = 0; i < 4; ++i) out_buffer[offset++] = track_header[i];
    
    int32_t size_offset = offset;
    offset += 4; // Skip 4 bytes for size

    // 3. Encode Events
    for (int i = 0; i < num_events; ++i) {
        if (offset + 8 >= max_buffer_size) {
            *err_code = -2; // Buffer overflow
            return;
        }

        int32_t pitch = note_events[i * 3];
        int32_t vel = note_events[i * 3 + 1];
        int32_t dur = note_events[i * 3 + 2];

        // Delta time (0 for Note On in this deterministic layout)
        out_buffer[offset++] = 0x00;
        
        // Note On (Channel 1)
        out_buffer[offset++] = 0x90;
        out_buffer[offset++] = (uint8_t)(pitch & 0x7F);
        out_buffer[offset++] = (uint8_t)(vel & 0x7F);

        // Delta time for Note Off (Simplified Variable Length Quantity for dur <= 127)
        out_buffer[offset++] = (uint8_t)(dur & 0x7F); 
        
        // Note Off (Channel 1)
        out_buffer[offset++] = 0x80;
        out_buffer[offset++] = (uint8_t)(pitch & 0x7F);
        out_buffer[offset++] = 0x00; // Vel 0
    }

    // 4. End of Track Meta Event
    if (offset + 4 >= max_buffer_size) {
        *err_code = -2;
        return;
    }
    out_buffer[offset++] = 0x00; // Delta 0
    out_buffer[offset++] = 0xFF; // Meta
    out_buffer[offset++] = 0x2F; // End of Track
    out_buffer[offset++] = 0x00; // Length 0

    // 5. Backfill Track Size
    int32_t track_size = offset - size_offset - 4;
    out_buffer[size_offset] = (uint8_t)((track_size >> 24) & 0xFF);
    out_buffer[size_offset + 1] = (uint8_t)((track_size >> 16) & 0xFF);
    out_buffer[size_offset + 2] = (uint8_t)((track_size >> 8) & 0xFF);
    out_buffer[size_offset + 3] = (uint8_t)(track_size & 0xFF);

    *bytes_written = offset;
    *err_code = 0;
}

}
