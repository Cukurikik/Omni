// ==========================================
// 📡 OMNI-LAND: GOLANG CHANNEL EVENT EMITTER
// ==========================================
// Node.js EventEmitter berjalan di single-thread JS.
// OMNI EventEmitter menggunakan Golang Channels — setiap
// event di-dispatch ke Goroutine terpisah (multi-threaded).
//
// IMPORT: import { OmniEmitter } from 'omni/events';
// ==========================================

declare const OmniNative: {
    syscall: (command: string, args: Record<string, unknown>) => Record<string, unknown>;
    registerCallback: (id: string, fn: Function) => void;
};

/**
 * OmniEmitter — Golang Channel-backed Event Emitter.
 * Setiap instance membuat Go channel baru di memori.
 * Event di-emit secara asinkron melalui Goroutines.
 */
export class OmniEmitter {
    private channelId: string;
    private _localListeners: Map<string, Array<(data: any) => void>> = new Map();

    constructor(name: string) {
        const res = OmniNative.syscall("event_create_channel", { name });
        this.channelId = res.channelId as string;
    }

    /**
     * Daftarkan listener untuk event tertentu.
     * Listener di-register ke Golang Channel via callback bridge.
     */
    on(event: string, listener: (data: any) => void): this {
        // Register ke Go-side
        OmniNative.registerCallback(`event_${this.channelId}_${event}`, listener);

        // Simpan juga di local map untuk off() dan listenerCount()
        if (!this._localListeners.has(event)) {
            this._localListeners.set(event, []);
        }
        this._localListeners.get(event)!.push(listener);

        OmniNative.syscall("event_subscribe", {
            channelId: this.channelId,
            event,
            callbackId: `event_${this.channelId}_${event}`,
        });

        return this;
    }

    /**
     * Daftarkan listener yang hanya dipanggil SEKALI.
     */
    once(event: string, listener: (data: any) => void): this {
        const wrapper = (data: any) => {
            this.off(event, wrapper);
            listener(data);
        };
        return this.on(event, wrapper);
    }

    /**
     * Emit event — data dikirim ke Golang Channel.
     * ⚡ SPEK DEWA: Data diproses oleh inti CPU lain via Goroutine!
     */
    emit(event: string, data?: any): boolean {
        const listeners = this._localListeners.get(event);
        const hasListeners = listeners !== undefined && listeners.length > 0;

        OmniNative.syscall("event_emit", {
            channelId: this.channelId,
            event,
            data: data ?? null,
        });

        return hasListeners;
    }

    /**
     * Hapus listener tertentu dari event.
     */
    off(event: string, listener: (data: any) => void): this {
        const listeners = this._localListeners.get(event);
        if (listeners) {
            const idx = listeners.indexOf(listener);
            if (idx !== -1) {
                listeners.splice(idx, 1);
            }
        }
        return this;
    }

    /**
     * Hapus SEMUA listener dari event (atau semua event jika tidak dispesifikasikan).
     */
    removeAllListeners(event?: string): this {
        if (event) {
            this._localListeners.delete(event);
        } else {
            this._localListeners.clear();
        }
        OmniNative.syscall("event_remove_all", {
            channelId: this.channelId,
            event: event || "__all__",
        });
        return this;
    }

    /**
     * Jumlah listener terdaftar untuk event tertentu.
     */
    listenerCount(event: string): number {
        return this._localListeners.get(event)?.length ?? 0;
    }

    /**
     * Daftar semua nama event yang memiliki listener.
     */
    eventNames(): string[] {
        return Array.from(this._localListeners.keys());
    }

    /**
     * Destroy channel — bebaskan Go channel dari memori.
     */
    destroy(): void {
        OmniNative.syscall("event_destroy_channel", { channelId: this.channelId });
        this._localListeners.clear();
    }
}

export default OmniEmitter;
