// OMNI UI & Mobile Layer
// React Native Mobile Bridge
// Based on facebook/react-native. Allows mobile apps to interface with the Omni Universal Binary
// running natively via JNI (Android) or Objective-C++ (iOS).

import { NativeModules, NativeEventEmitter, Platform } from 'react-native';

const { OmniUniversalModule } = NativeModules;
const omniEmitter = new NativeEventEmitter(OmniUniversalModule);

export interface OmniTaskResult {
    taskId: string;
    status: 'success' | 'failed';
    data?: any;
    error?: string;
}

export class OmniReactNativeBridge {
    constructor() {
        console.log(`OMNI TS: Initializing React Native Bridge on ${Platform.OS}`);
        if (!OmniUniversalModule) {
            console.warn("OMNI Warning: Native module not linked. Running in mock/fallback mode.");
        }
    }

    /**
     * Executes a high-performance compute task directly on the mobile device's NPU/GPU
     * via the Omni Universal Binary.
     */
    public async executeNativeTask(taskName: string, payload: any): Promise<OmniTaskResult> {
        if (!OmniUniversalModule) {
            return Promise.reject("Omni Native Module unavailable.");
        }

        try {
            console.log(`OMNI TS: Dispatching ${taskName} to C-ABI via JNI/ObjC...`);
            const serializedPayload = JSON.stringify(payload);
            const resultStr = await OmniUniversalModule.executeTask(taskName, serializedPayload);
            return JSON.parse(resultStr);
        } catch (error) {
            console.error(`OMNI TS Error: Native task execution failed:`, error);
            throw error;
        }
    }

    /**
     * Subscribes to real-time events emitted by the native C++ engine (e.g., download progress, streaming inference)
     */
    public subscribeToEngineEvents(callback: (event: any) => void) {
        return omniEmitter.addListener('OmniEngineEvent', callback);
    }
}

// Example hook for React Native components
// export function useOmniEngine() {
//     const [bridge] = useState(() => new OmniReactNativeBridge());
//     return bridge;
// }
