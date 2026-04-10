# Script to generate interfaces for Tasks 11-25 (Klasifikasi B)
$omniMod = "c:\Users\IKYY\Downloads\Omni\omni-runtime\omni_modules"

function Ensure-Directory {
    param([string]$path)
    if (-not (Test-Path $path)) {
        New-Item -ItemType Directory -Force -Path $path | Out-Null
    }
}

$interfaces = @{
    "omni-fs-core" = @"
/// [OMNI-INTERFACE] Task 11: File System Core (Sync Operations)
/// Replaces: node:fs (Sync methods)
export interface FsCore {
    fn readFileSync(path: String) -> Buffer;
    fn writeFileSync(path: String, data: Buffer) -> void;
    fn chmodSync(path: String, mode: Number) -> void;
    fn statSync(path: String) -> FileStats;
}
"@

    "omni-fs-async" = @"
/// [OMNI-INTERFACE] Task 12: File System Async (Non-Blocking)
/// Replaces: node:fs/promises
export interface FsAsync {
    fn readFile(path: String) -> Promise<Buffer>;
    fn writeFile(path: String, data: Buffer) -> Promise<void>;
    fn appendFile(path: String, data: Buffer) -> Promise<void>;
}
"@

    "omni-path" = @"
/// [OMNI-INTERFACE] Task 13: Path Manipulation
/// Replaces: node:path
export interface PathOps {
    fn join(...paths: String) -> String;
    fn resolve(...paths: String) -> String;
    fn basename(path: String, ext: String = "") -> String;
    fn dirname(path: String) -> String;
}
"@

    "omni-os" = @"
/// [OMNI-INTERFACE] Task 14: Operating System Utilities
/// Replaces: node:os
export interface OSInfo {
    fn cpus() -> Vec<CpuInfo>;
    fn totalmem() -> Number;
    fn freemem() -> Number;
    fn platform() -> String;
    fn arch() -> String;
    fn uptime() -> Number;
}
"@

    "omni-process" = @"
/// [OMNI-INTERFACE] Task 15: OS Process & Signals
/// Replaces: node:process
export interface ProcessControl {
    fn exit(code: Number = 0) -> void;
    fn cwd() -> String;
    fn memoryUsage() -> MemoryUsage;
    fn on(signal: String, handler: fn() -> void) -> void;
}
"@

    "omni-child" = @"
/// [OMNI-INTERFACE] Task 16: Spawning and Executing Sub-processes
/// Replaces: node:child_process
export interface ChildFactory {
    fn spawn(command: String, args: Vec<String>, options: Object = {}) -> ChildProcess;
    fn exec(command: String) -> Promise<ExecResult>;
    fn fork(modulePath: String) -> ChildProcess;
}
"@

    "omni-tty" = @"
/// [OMNI-INTERFACE] Task 17: Teletype / Terminal Formatting
/// Replaces: node:tty
export interface TTY {
    fn isatty(fd: Number) -> bool;
    fn columns() -> Number;
    fn rows() -> Number;
}
"@

    "omni-stream-io" = @"
/// [OMNI-INTERFACE] Task 18: Stream I/O Operations
/// Replaces: node:stream
export interface StreamIO {
    fn createReadStream(path: String) -> ReadableStream;
    fn createWriteStream(path: String) -> WritableStream;
    fn pipeline(...streams: Stream) -> Promise<void>;
}
"@

    "omni-readline" = @"
/// [OMNI-INTERFACE] Task 19: Interactive Readline Interface
/// Replaces: node:readline
export interface Readline {
    fn question(query: String) -> Promise<String>;
    fn prompt() -> void;
    fn close() -> void;
}
"@

    "omni-net-tcp" = @"
/// [OMNI-INTERFACE] Task 20: Native TCP Socket Server
/// Replaces: node:net
export interface NetTCP {
    fn createServer(connectionListener: fn(Socket) -> void) -> TCPServer;
    fn connect(port: Number, host: String) -> Socket;
}
"@

    "omni-net-udp" = @"
/// [OMNI-INTERFACE] Task 21: Bare UDP Datagram Sockets
/// Replaces: node:dgram
export interface NetUDP {
    fn createSocket(type: String) -> UIDPSocket;
    fn send(msg: Buffer, port: Number, address: String) -> void;
}
"@

    "omni-dns" = @"
/// [OMNI-INTERFACE] Task 22: DNS Lookup and Resolution
/// Replaces: node:dns
export interface DNSNetwork {
    fn lookup(hostname: String) -> Promise<IPv4>;
    fn resolveMx(hostname: String) -> Promise<Vec<MxRecord>>;
    fn resolveTxt(hostname: String) -> Promise<Vec<String>>;
}
"@

    "omni-crypto-hash" = @"
/// [OMNI-INTERFACE] Task 23: Hardware-accelerated Hashing
/// Part of node:crypto replacements
export interface CryptoHash {
    fn createHash(algorithm: String) -> Hasher;
    fn pbkdf2(password: String, salt: String, iterations: Number, keylen: Number) -> Promise<Buffer>;
}
"@

    "omni-crypto-tls" = @"
/// [OMNI-INTERFACE] Task 24: TLS / SSL Authenticated Transport
/// Replaces: node:tls
export interface CryptoTLS {
    fn connect(options: TlsOptions) -> TLSSocket;
    fn createServer(options: TlsOptions, secureConnectionListener: fn(TLSSocket) -> void) -> TLSServer;
}
"@

    "omni-compress" = @"
/// [OMNI-INTERFACE] Task 25: Native Zlib Compression
/// Replaces: node:zlib
export interface Compressor {
    fn gzip(buffer: Buffer) -> Promise<Buffer>;
    fn gunzip(buffer: Buffer) -> Promise<Buffer>;
    fn deflate(buffer: Buffer) -> Promise<Buffer>;
    fn inflate(buffer: Buffer) -> Promise<Buffer>;
    fn createGzip() -> TransformStream;
}
"@
}

foreach ($key in $interfaces.Keys) {
    $dirPath = [System.IO.Path]::Combine($omniMod, $key, "src")
    Ensure-Directory $dirPath
    $filePath = [System.IO.Path]::Combine($dirPath, "lib.omni")
    Set-Content -Path $filePath -Value $interfaces[$key] -Encoding UTF8
    Write-Host "Generated OS Module: $key"
}
Write-Host "Batch Task 11-25 Completed!"
