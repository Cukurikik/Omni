// ==========================================
// 📦 OMNI UI — Barrel Export (ES2026 Sovereign Edition)
// ==========================================
// Semua modul OMNI diakses melalui satu pintu.
// import { OmniRouter, OmniLink, OmniClient, useOmniSSR, useOmniStream } from '../omni';

export { OmniRouter, OmniRoutes, OmniLink, useOmniRouter, useOmniNavigate, useOmniParams, omniNavigate } from './OmniRouter';
export type { OmniRoute } from './OmniRouter';
export { OmniClient, createOmniSocket } from './OmniClient';
export type { OmniJobResult, OmniJobStatus } from './OmniClient';
export { useOmniSSR, getOmniSSRState, hasOmniSSR } from './useOmniSSR';

// 🚀 ES2026: Explicit Resource Management + Streaming
export { useOmniStream, connectToTitanBuffer } from './useOmniStream';
export type { StreamMessage, StreamProgress, ConnectionState } from './useOmniStream';

// 🧬 ES2026: Immutable Records & Tuples
export {
    deepFreeze,
    createImmutableRecord,
    createImmutableTuple,
    createServerState,
    OmniStateGuard,
} from './OmniState';
export type { ServerState } from './OmniState';
