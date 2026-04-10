// ==========================================
// 🌐 OMNI-LAND: NATIVE TCP/UDP SOCKETS
// ==========================================
// Node.js net module → libuv event loop
// OMNI net module → Go net.Conn + Goroutines
//
// IMPORT: import { net } from 'omni/net';
// ==========================================

declare const OmniNative: {
    syscall: (command: string, args: Record<string, unknown>) => Record<string, unknown>;
    registerCallback: (id: string, fn: Function) => void;
};

/**
 * Buat TCP server yang mendengarkan pada port tertentu.
 * ⚡ Setiap koneksi = 1 Goroutine — PARALEL SEJATI.
 */
export function createTCPServer(
    port: number,
    handler: (conn: { remoteAddr: string; data: string }) => string,
): string {
    const callbackId = `tcp_handler_${port}`;
    OmniNative.registerCallback(callbackId, handler);
    const res = OmniNative.syscall("net_tcp_listen", { port, callbackId });
    if (res.error) throw new Error(`[OMNI-NET] ${res.error}`);
    return res.serverId as string;
}

/**
 * Buat koneksi TCP client ke remote host.
 */
export function connect(host: string, port: number, options?: {
    timeout?: number;
}): string {
    const res = OmniNative.syscall("net_tcp_connect", {
        host,
        port,
        timeout: options?.timeout ?? 30000,
    });
    if (res.error) throw new Error(`[OMNI-NET] ${res.error}`);
    return res.connId as string;
}

/**
 * Kirim data melalui koneksi TCP.
 */
export function send(connId: string, data: string): void {
    const res = OmniNative.syscall("net_tcp_send", { connId, data });
    if (res.error) throw new Error(`[OMNI-NET] ${res.error}`);
}

/**
 * Tutup koneksi TCP.
 */
export function close(connId: string): void {
    OmniNative.syscall("net_tcp_close", { connId });
}

/**
 * Buat UDP socket untuk mengirim/menerima datagram.
 */
export function createUDPSocket(port: number): string {
    const res = OmniNative.syscall("net_udp_bind", { port });
    if (res.error) throw new Error(`[OMNI-NET] ${res.error}`);
    return res.socketId as string;
}

/**
 * Kirim UDP datagram.
 */
export function sendUDP(socketId: string, host: string, port: number, data: string): void {
    const res = OmniNative.syscall("net_udp_send", { socketId, host, port, data });
    if (res.error) throw new Error(`[OMNI-NET] ${res.error}`);
}

/**
 * Cek apakah port tersedia (tidak dipakai proses lain).
 */
export function isPortAvailable(port: number): boolean {
    const res = OmniNative.syscall("net_port_check", { port });
    return res.available as boolean;
}

export const net = {
    createTCPServer,
    connect,
    send,
    close,
    createUDPSocket,
    sendUDP,
    isPortAvailable,
};

export default net;
