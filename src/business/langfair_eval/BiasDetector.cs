using Omni.Core;

namespace LangFair {
    public class BiasDetector {
        public Result<bool, string> Detect(string text) {
            if (string.IsNullOrWhiteSpace(text)) return Result<bool, string>.Err("Text is empty");
            return Result<bool, string>.Ok(text.Contains("forbidden"));
        }
    }
}
