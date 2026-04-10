// ==========================================
// 🧬 OMNI-STATE: Immutable State Guardian (ES2026 Pattern)
// ==========================================
// Implementasi filosofi Immutable Records & Tuples dari ES2026.
//
// FILOSOFI:
//   Data yang ditarik dari Golang SSD/RAM TIDAK BOLEH dimanipulasi
//   secara sembarangan di sisi UI. State server bersifat SAKRAL — 
//   hanya bisa dibaca, tidak bisa di-hack.
//
// MEKANISME:
//   - deepFreeze() → Membekukan objek secara rekursif (seluruh nested level)
//   - createImmutableRecord() → ES2026 Immutable Record pattern
//   - createImmutableTuple() → ES2026 Immutable Tuple pattern
//   - OmniStateGuard → Kelas penjaga yang membungkus state server
//
// KOMPATIBILITAS:
//   Records (#{}), Tuples (#[]) belum tersedia di semua runtime.
//   Kita menggunakan Object.freeze + Proxy sebagai polyfill yang
//   memberikan perilaku identik: throw error jika dimutasi.
// ==========================================

/**
 * deepFreeze — Membekukan objek secara mendalam (rekursif).
 * Setelah di-freeze, setiap attempt mutasi akan throw TypeError di strict mode.
 *
 * @example
 * ```ts
 * const state = deepFreeze({ user: { name: "OMNI" } });
 * state.user.name = "HACKED"; // ❌ TypeError di strict mode!
 * ```
 */
export function deepFreeze<T extends object>(obj: T): Readonly<T> {
    Object.freeze(obj);

    for (const key of Object.getOwnPropertyNames(obj)) {
        const value = (obj as Record<string, unknown>)[key];
        if (value !== null && typeof value === 'object' && !Object.isFrozen(value)) {
            deepFreeze(value as object);
        }
    }

    return obj as Readonly<T>;
}

/**
 * createImmutableRecord — ES2026 Record polyfill.
 * Membungkus objek dengan Proxy yang MENOLAK semua operasi tulis.
 *
 * Bedanya dengan Object.freeze:
 *   - freeze: throw di strict mode, silent fail di sloppy mode
 *   - Proxy: SELALU throw di semua mode + pesan error yang jelas
 *
 * @example
 * ```ts
 * const serverState = createImmutableRecord({
 *     status: "PROCESSING",
 *     titanBufferUsed: "8GB",
 *     activeWorkers: ["python_vision", "rust_encoder"],
 * });
 *
 * serverState.status = "HACKED"; // ❌ TypeError: OMNI-STATE: Mutasi terlarang!
 * ```
 */
export function createImmutableRecord<T extends object>(data: T): Readonly<T> {
    const frozen = deepFreeze(structuredClone(data));

    return new Proxy(frozen, {
        set(_target, prop) {
            throw new TypeError(
                `🛡️ [OMNI-STATE] Mutasi terlarang pada property "${String(prop)}"! ` +
                `State server bersifat IMMUTABLE. Gunakan createImmutableRecord() untuk membuat state baru.`
            );
        },
        deleteProperty(_target, prop) {
            throw new TypeError(
                `🛡️ [OMNI-STATE] Penghapusan terlarang pada property "${String(prop)}"! ` +
                `State server tidak boleh dihapus.`
            );
        },
    }) as Readonly<T>;
}

/**
 * createImmutableTuple — ES2026 Tuple polyfill.
 * Membungkus array dengan Proxy yang MENOLAK push, pop, splice, atau mutasi apapun.
 *
 * @example
 * ```ts
 * const workers = createImmutableTuple(["ffmpeg", "python_ai", "rust_encoder"]);
 * workers.push("hacker_tool"); // ❌ TypeError!
 * workers[0] = "malware";      // ❌ TypeError!
 * ```
 */
export function createImmutableTuple<T>(data: readonly T[]): readonly T[] {
    const frozen = Object.freeze([...data]);

    return new Proxy(frozen, {
        set(_target, prop) {
            throw new TypeError(
                `🛡️ [OMNI-STATE] Mutasi terlarang pada index "${String(prop)}"! ` +
                `Tuple bersifat IMMUTABLE. Buat tuple baru dengan createImmutableTuple().`
            );
        },
        deleteProperty(_target, prop) {
            throw new TypeError(
                `🛡️ [OMNI-STATE] Penghapusan terlarang pada index "${String(prop)}"!`
            );
        },
    }) as readonly T[];
}

// ==========================================
// 🛡️ OMNI-STATE GUARD: Server State Protection
// ==========================================

export interface ServerState {
    /** Status pemrosesan */
    status: string;
    /** Buffer Titan yang sedang dipakai */
    titanBufferUsed: string;
    /** Worker yang sedang aktif */
    activeWorkers: readonly string[];
    /** Timestamp dari server */
    timestamp: number;
    /** Data tambahan */
    [key: string]: unknown;
}

/**
 * OmniStateGuard — Kelas penjaga yang membungkus state dari server Golang.
 * State di-freeze saat diterima dan hanya bisa diperbarui melalui .update().
 *
 * @example
 * ```ts
 * const guard = new OmniStateGuard({
 *     status: "PROCESSING",
 *     titanBufferUsed: "8GB",
 *     activeWorkers: ["ffmpeg", "onnx"],
 *     timestamp: Date.now(),
 * });
 *
 * // Baca (OK)
 * console.log(guard.state.status); // "PROCESSING"
 *
 * // Mutasi langsung (DIBLOKIR)
 * guard.state.status = "HACKED"; // ❌ TypeError!
 *
 * // Update resmi (OK — menghasilkan RECORD BARU)
 * const newGuard = guard.update({ status: "SUCCESS" });
 * console.log(newGuard.state.status); // "SUCCESS"
 * ```
 */
export class OmniStateGuard {
    public readonly state: Readonly<ServerState>;
    private readonly _history: readonly Readonly<ServerState>[];

    constructor(initialState: ServerState, previousHistory?: readonly Readonly<ServerState>[]) {
        this.state = createImmutableRecord(initialState);
        this._history = createImmutableTuple(
            previousHistory
                ? [...previousHistory, this.state]
                : [this.state]
        );
    }

    /**
     * Buat state baru dengan perubahan yang diberikan.
     * State lama TIDAK berubah — Immutable!
     */
    update(patch: Partial<ServerState>): OmniStateGuard {
        const newState: ServerState = {
            ...structuredClone(this.state) as ServerState,
            ...patch,
            timestamp: Date.now(),
        };
        // Buat guard baru dengan riwayat yang di-extend (clean construction)
        return new OmniStateGuard(newState, this._history);
    }

    /**
     * Ambil seluruh riwayat state (time-travel debugging).
     */
    get history(): readonly Readonly<ServerState>[] {
        return this._history;
    }

    /**
     * Jumlah perubahan yang terjadi.
     */
    get version(): number {
        return this._history.length;
    }
}

// ==========================================
// 🏭 FACTORY: Quick Immutable State
// ==========================================

/**
 * createServerState — Buat immutable server state dari raw JSON response.
 *
 * @example
 * ```ts
 * const res = await fetch('/api/v1/omni/metrics');
 * const raw = await res.json();
 * const state = createServerState(raw);
 * // state sekarang immutable — aman dari XSS state injection
 * ```
 */
export function createServerState(rawData: Record<string, unknown>): Readonly<ServerState> {
    return createImmutableRecord({
        status: String(rawData.status || 'UNKNOWN'),
        titanBufferUsed: String(rawData.titan_buffer_used || '0B'),
        activeWorkers: createImmutableTuple(
            Array.isArray(rawData.active_workers) ? rawData.active_workers : []
        ) as unknown as readonly string[],
        timestamp: Number(rawData.timestamp) || Date.now(),
        ...rawData,
    });
}
