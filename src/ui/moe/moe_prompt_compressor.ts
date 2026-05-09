// moe_prompt_compressor.ts — Interface / Optimization
// Layer: Interface / API — Client-Side Prompt Compression
//
// Extremely long prompts cost tenants money and waste MoE bandwidth.
// This TypeScript module implements a client-side Lempel-Ziv-Welch (LZW) 
// compression algorithm tailored for text payload compression BEFORE it is
// transmitted to the Go Gateway over the network.

export class PromptCompressor {
    constructor() {
        console.log("[Prompt Compressor] Initialized client-side LZW compression engine.");
    }

    /**
     * Compresses a string using the LZW algorithm.
     * Generates an array of 16-bit integer codes.
     */
    public compress(uncompressed: string): number[] {
        if (!uncompressed) return [];

        // Build the dictionary
        const dictionary: Map<string, number> = new Map();
        for (let i = 0; i < 256; i++) {
            dictionary.set(String.fromCharCode(i), i);
        }

        let currentString = "";
        const compressedData: number[] = [];
        let dictSize = 256;

        for (let i = 0; i < uncompressed.length; i++) {
            const char = uncompressed.charAt(i);
            const combinedString = currentString + char;

            if (dictionary.has(combinedString)) {
                currentString = combinedString;
            } else {
                compressedData.push(dictionary.get(currentString)!);
                
                // Add combinedString to dictionary if space permits (16-bit limit)
                if (dictSize < 65536) {
                    dictionary.set(combinedString, dictSize++);
                }
                currentString = char;
            }
        }

        if (currentString !== "") {
            compressedData.push(dictionary.get(currentString)!);
        }

        const originalBytes = uncompressed.length * 2; // UTF-16
        const compressedBytes = compressedData.length * 2;
        const ratio = ((1 - (compressedBytes / originalBytes)) * 100).toFixed(2);
        
        console.log(`[Prompt Compressor] Compressed payload by ${ratio}%. Transmitting efficient payload.`);
        return compressedData;
    }

    /**
     * Decompresses the LZW encoded payload.
     * Normally this is executed on the Go Gateway server.
     */
    public decompress(compressedData: number[]): string {
        if (!compressedData || compressedData.length === 0) return "";

        const dictionary: string[] = [];
        for (let i = 0; i < 256; i++) {
            dictionary[i] = String.fromCharCode(i);
        }

        let currentCode = compressedData[0];
        let currentString = String.fromCharCode(currentCode);
        let decompressed = currentString;
        let dictSize = 256;

        for (let i = 1; i < compressedData.length; i++) {
            const code = compressedData[i];
            let entry = "";

            if (dictionary[code] !== undefined) {
                entry = dictionary[code];
            } else if (code === dictSize) {
                entry = currentString + currentString.charAt(0);
            } else {
                throw new Error("Invalid compressed stream");
            }

            decompressed += entry;

            if (dictSize < 65536) {
                dictionary[dictSize++] = currentString + entry.charAt(0);
            }

            currentString = entry;
        }

        return decompressed;
    }
}
