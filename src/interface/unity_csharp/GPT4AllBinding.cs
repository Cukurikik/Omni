using System;
using System.Runtime.InteropServices;

namespace Omni.GPT4AllUnity {
    public class GPT4AllModel : IDisposable {
        [DllImport("omni_gpt4all")]
        private static extern IntPtr gpt4all_load_model(string path);
        
        [DllImport("omni_gpt4all")]
        private static extern int gpt4all_generate(IntPtr ctx, string prompt, byte[] outBuf, int maxLen);
        
        private IntPtr _ctx;
        
        public GPT4AllModel(string path) {
            _ctx = gpt4all_load_model(path);
            if (_ctx == IntPtr.Zero) throw new Exception("OmniError: Failed to load model");
        }
        
        public void Dispose() {
            // cleanup
        }
    }
}
