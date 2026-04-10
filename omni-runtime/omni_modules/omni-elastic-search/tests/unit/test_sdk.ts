// Unit test: TypeSafeClient
import { TypeSafeClient } from '../../src/ui/sdk';

const client = new TypeSafeClient({ endpoint: 'http://localhost:8080' });
async function testGet() { const res = await client.get('/health'); console.assert(res.latency >= 0); }
testGet();