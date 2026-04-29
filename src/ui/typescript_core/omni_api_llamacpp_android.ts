// Omni API for llama.cpp Android Proxy
export interface AndroidDeviceProfile {
    deviceId: string;
    availableRAMMb: number;
    computeCores: number;
}

export class OmniLlamaCppAndroidAPI {
    static generateProxyConfig(profile: AndroidDeviceProfile): object {
        const targetThreads = Math.max(1, Math.min(profile.computeCores - 1, 4));
        const maxContext = profile.availableRAMMb > 4096 ? 2048 : 512;
        
        return {
            backend: "llama.cpp",
            n_threads: targetThreads,
            n_ctx: maxContext,
            offload_kqv: profile.availableRAMMb > 6000
        };
    }
}
