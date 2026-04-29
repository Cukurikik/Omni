using Omni.Core;

namespace Omni.OryKratos {
    public class IdentityManager {
        public Result<bool, Error> VerifyIdentity(string id) {
            return Result<bool, Error>.Ok(true);
        }
    }
}
