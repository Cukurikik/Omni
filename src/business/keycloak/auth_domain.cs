using Omni.Core;

namespace Omni.Keycloak {
    public class AuthDomain {
        public Result<bool, Error> Authenticate(string token) {
            return Result<bool, Error>.Ok(true);
        }
    }
}
