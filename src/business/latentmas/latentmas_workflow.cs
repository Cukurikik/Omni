using System;
using System.Collections.Generic;
// @omni-domain Business Layer (LatentMAS Workflow)
namespace Omni.Business.LatentMAS {
    public class OmniResult<T> { public T Data; public Exception Error; public bool IsOk => Error==null;
        public static OmniResult<T> Ok(T d)=>new(){Data=d}; public static OmniResult<T> Err(Exception e)=>new(){Error=e}; }
    public class LatentMASWorkflow {
        private List<Func<Dictionary<string,object>,OmniResult<Dictionary<string,object>>>> _steps = new();
        public void AddStep(Func<Dictionary<string,object>,OmniResult<Dictionary<string,object>>> step) => _steps.Add(step);
        public OmniResult<Dictionary<string,object>> Execute(Dictionary<string,object> context) {
            try { var ctx = context;
                foreach (var step in _steps) { var r = step(ctx); if (!r.IsOk) return r; ctx = r.Data; }
                return OmniResult<Dictionary<string,object>>.Ok(ctx);
            } catch(Exception e) { return OmniResult<Dictionary<string,object>>.Err(e); }
        }
    }
}
