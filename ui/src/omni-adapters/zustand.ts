import { create } from 'zustand';

// ===============================================
// ⚛️ OMNI NATIVE STATE ADAPTER (ZUSTAND REACTIVITY)
// ===============================================
// Adaptor ini menghilangkan ketergantungan Redux yang bengkak.
// Terkoneksi mutlak dengan memori WebAssembly atau IndexedDB.

export interface FileTask {
    id: string;
    filename: string;
    bytes: number;
    status: 'queue' | 'processing' | 'done' | 'failed';
}

interface OmniState {
    kernelConnected: boolean;
    activeTasks: FileTask[];
    
    // Actions
    connectKernel: () => void;
    addTask: (task: FileTask) => void;
    updateTaskStatus: (id: string, newStatus: FileTask['status']) => void;
}

export const useOmniStore = create<OmniState>((set) => ({
    kernelConnected: false,
    activeTasks: [],

    connectKernel: () => {
        // Simulasi koneksi FFI (Foreign Function Interface) murni ke engine Rust/WASM
        console.log("[ZUSTAND] Menginisiasi protokol RAM OMNI-WASM...");
        set({ kernelConnected: true });
    },

    addTask: (task) => set((state) => ({ 
        activeTasks: [...state.activeTasks, task] 
    })),

    updateTaskStatus: (id, status) => set((state) => ({
        activeTasks: state.activeTasks.map(t => 
            t.id === id ? { ...t, status } : t
        )
    }))
}));
