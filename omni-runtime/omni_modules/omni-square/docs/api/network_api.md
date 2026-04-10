# omni-square - Network API Reference

## ConnectionPool
- Acquire(ctx) - Get connection from pool
- Release(conn) - Return connection
- Stats() - Pool statistics
- Drain() - Drain all connections

## ProtocolHandler
- Encode(msg) - Encode message to wire format
- Decode(reader) - Decode message from wire

## TransportLayer
- Connect(ctx) - Establish TCP/TLS connection
- Send(data) - Send raw bytes
- Recv(buf) - Receive raw bytes