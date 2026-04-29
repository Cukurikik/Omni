using System;
using System.Collections.Generic;
namespace OmniBatch9.Business {
    public struct OmniResult<T> {
        public bool IsOk; public T Value; public string Error;
        public static OmniResult<T> Ok(T v) => new OmniResult<T>{IsOk=true,Value=v,Error=null};
        public static OmniResult<T> Fail(string e) => new OmniResult<T>{IsOk=false,Value=default,Error=e};
    }
    public class LLMBlenderFusionEngine {
        const int MAX_CANDIDATES = 50;
        public OmniResult<string> FuseResponses(string prompt, List<string> ranked, int topK) {
            if (string.IsNullOrEmpty(prompt)) return OmniResult<string>.Fail("Empty prompt");
            if (ranked == null || ranked.Count == 0) return OmniResult<string>.Fail("No candidates");
            if (topK > MAX_CANDIDATES) return OmniResult<string>.Fail($"TopK exceeds {MAX_CANDIDATES}");
            var selected = ranked.GetRange(0, Math.Min(topK, ranked.Count));
            var fused = string.Join(" ", selected);
            return OmniResult<string>.Ok(fused);
        }
    }
}
