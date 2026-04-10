// ==========================================
// ⚛️ OMNI-LAND: STANDARD LIBRARY — 40+ MODUL INTI
// ==========================================
// Barrel exports untuk seluruh OMNI Standard Library.
// Setiap modul adalah TypeScript wrapper yang memanggil
// Golang Standard Library via OmniNative.syscall().
//
// OMNI-JS menggantikan 5.000 file C++ Node.js
// dengan ~20 file TypeScript + 1 file Go syscall router.
// ==========================================

// ==========================================
// 📂 FILE SYSTEM (Node.js: fs)
// ==========================================
export { 
    readFileSync, writeFileSync, existsSync, 
    mkdirSync, readdirSync, removeSync, statSync 
} from './fs';

// ==========================================
// 🗺️ PATH (Node.js: path)
// ==========================================
export { 
    join, resolve, extname, basename, dirname, 
    normalize, isAbsolute, relative, parse as parsePath, 
    sep, delimiter 
} from './path';
export { path } from './path';

// ==========================================
// 🖥️ OS (Node.js: os)
// ==========================================
export { 
    arch, platform, cpus, totalmem, freemem,
    hostname, homedir, tmpdir, uptime, eol, 
    env, getenv, pid, info as osInfo 
} from './os';
export { os } from './os';

// ==========================================
// 📡 EVENTS (Node.js: events)
// ==========================================
export { OmniEmitter } from './events';

// ==========================================
// 🛡️ CRYPTO (Node.js: crypto)
// ==========================================
export { 
    hash, hmacSign, hmacVerify,
    encryptAES, decryptAES,
    randomUUID, randomBytes, randomInt,
    pbkdf2, bcryptHash, bcryptVerify,
    generateKeyPair, sign, verify 
} from './crypto';
export { crypto } from './crypto';

// ==========================================
// 🌐 HTTP (Node.js: http/https)
// ==========================================
export { serve, fetch, postJSON, getJSON } from './http';
export type { OmniRequest, OmniResponse, OmniHandler, FetchOptions, FetchResponse } from './http';

// ==========================================
// ⏱️ TIMERS (Node.js: timers)
// ==========================================
export { 
    setTimeout, clearTimeout, 
    setInterval, clearInterval, 
    sleep, hrtime 
} from './timers';

// ==========================================
// 🔄 STREAMS (Node.js: stream)
// ==========================================
export { 
    createReadStream, createWriteStream, 
    streamWrite, streamClose, 
    onData, onEnd, onError, 
    pipeline, copyFile 
} from './stream';

// ==========================================
// 🧱 BUFFER (Node.js: buffer)
// ==========================================
export { 
    toBase64, fromBase64, toHex, fromHex,
    byteLength, concat, compare, transcode 
} from './buffer';
export { buffer } from './buffer';

// ==========================================
// 🔗 URL (Node.js: url)
// ==========================================
export { 
    parse as parseURL, format as formatURL,
    resolve as resolveURL,
    encodeQuery, decodeQuery,
    encode as urlEncode, decode as urlDecode 
} from './url';
export { url } from './url';

// ==========================================
// ⚙️ PROCESS (Node.js: process)
// ==========================================
export { 
    exit, cwd, chdir, argv, 
    execPath, setenv, memoryUsage, version 
} from './process';
export { process } from './process';

// ==========================================
// 🚀 CHILD PROCESS (Node.js: child_process)
// ==========================================
export { execSync, exec, spawn, kill } from './child_process';

// ==========================================
// 🌐 TCP/UDP (Node.js: net)
// ==========================================
export { 
    createTCPServer, connect, send, close,
    createUDPSocket, sendUDP, isPortAvailable 
} from './tcp';
export { net } from './tcp';

// ==========================================
// 🔍 DNS (Node.js: dns)
// ==========================================
export { 
    lookup, reverse, 
    resolveMX, resolveTXT, resolveNS, resolveCNAME 
} from './dns';
export { dns } from './dns';

// ==========================================
// 📦 ZLIB (Node.js: zlib)
// ==========================================
export { 
    gzip, gunzip, deflate, inflate, 
    gzipFile, gunzipFile 
} from './zlib';
export { zlib } from './zlib';

// ==========================================
// 📋 CONSOLE (Node.js: console)
// ==========================================
export { 
    log, warn, error, debug, 
    table, time, timeEnd, timeLog,
    count, countReset 
} from './console';

// ==========================================
// 🧪 ASSERT (Node.js: assert)
// ==========================================
export { 
    ok, deepEqual, strictEqual, notEqual,
    throws, doesNotThrow, fail, match 
} from './assert';
export { assert } from './assert';

// ==========================================
// 🔧 UTIL (Node.js: util)
// ==========================================
export { 
    inspect, format,
    isArray, isString, isNumber, isBoolean, 
    isObject, isFunction, isNull, isUndefined,
    deepClone, deepMerge, debounce, throttle 
} from './util';
export { util } from './util';

// ==========================================
// 🧵 WORKER THREADS (Node.js: worker_threads)
// ==========================================
export { Worker, activeWorkerCount, getWorkerData, isMainThread } from './worker';

// ==========================================
// 🧬 QUERYSTRING (Node.js: querystring)
// ==========================================
export { querystring } from './querystring';

// ==========================================
// 📋 QUEUE (OMNI-AURA)
// ==========================================
export { dispatchBackgroundJob, onJob, getQueueStats } from './queue';

// ==========================================
// 🌍 MESH (OMNI-MESH P2P)
// ==========================================
export { joinGlobalMesh, broadcastState, onBroadcast, getMeshNodes, getMeshStats } from './mesh';

// ==========================================
// 🧠 AI (OMNI-MIND)
// ==========================================
export { askOmniMind, askOmniMindFull, awakenOmniMind, getAIStatus } from './ai';
export type { AIResponse, AIConfig } from './ai';

// ==========================================
// 🐍 PYTHON (OMNI-VENOM)
// ==========================================
export { runVenom, runPythonRaw, ignitePython, getVenomStatus } from './python';
export type { VenomResult, VenomStatus } from './python';

// ==========================================
// ⚛️ SYNAPSE (OMNI-SYNAPSE: JS ↔ FastAPI Bridge)
// ==========================================
export {
    igniteFastAPI, pyFetch, pyFetchFull,
    pyGet, pyPost, pyPut, pyDelete, pyPatch,
    getSynapseStatus, synapse
} from './synapse';
export type { SynapseResponse, SynapseConfig, SynapseStatus } from './synapse';

// ==========================================
// 🌐 NEXUS FETCH (OMNI-NEXUS: 5D Polyglot API Gateway)
// ==========================================
export {
    omniFetch, omniGet, omniPost, omniPut, omniDelete, omniPatch,
    omniFetchWithPython, omniFetchUnsafe,
    getNexusStatus, isOmniFetchOk, getOmniFetchError
} from './fetch';
export type {
    OmniFetchOptions, OmniFetchResponse, OmniFetchParsed,
    PythonCruncherConfig
} from './fetch';

// ==========================================
// 🐉 OMNI-LANG (The Unified Chimera Syntax)
// ==========================================
export { __omni_inline_exec } from './chimera';
