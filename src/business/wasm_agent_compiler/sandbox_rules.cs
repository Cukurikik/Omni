using System;

namespace Omni.Business.WasmAgentCompiler
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class SandboxRules
    {
        public OmniResult<bool> IsFeatureAllowedInBrowser(bool requires_raw_sockets, bool requires_file_system, bool requires_simd)
        {
            // WASM Business Logic: Browser Sandbox Constraints
            // WebAssembly runs in a strict sandbox. Agents must not rely on native OS capabilities.
            
            if (requires_raw_sockets)
            {
                // WebSockets are allowed, but raw TCP/UDP sockets are forbidden in WASM
                return new OmniResult<bool>(false);
            }
            
            if (requires_file_system)
            {
                // Local OS file system access is forbidden (must use OPFS or IndexedDB abstractions)
                return new OmniResult<bool>(false);
            }
            
            if (requires_simd)
            {
                // WASM SIMD is widely supported and allowed for high-performance AI inference
                return new OmniResult<bool>(true);
            }
            
            return new OmniResult<bool>(true);
        }
    }
}
