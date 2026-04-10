# omni-mojs - System API Reference

## NativeDriver
- boot(config) - Initialize the native driver
- connect() - Establish connection
- execute(query) - Execute a query
- execute_batch(queries) - Execute multiple queries
- close() - Close connection

## ArenaPool
- new(capacity) - Create memory arena
- alloc(size) - Allocate block
- reset() - Reset arena O(1) deallocation

## CryptoEngine
- encrypt(data) - AES-256-GCM encryption
- decrypt(payload) - Decryption
- hash_sha256(data) - SHA-256 hash
- hash_blake3(data) - BLAKE3 hash