using Omni.Core;

namespace KeycloakIam {
    public class TokenValidator {
        public Result<bool, string> Validate(string token) {
            if (string.IsNullOrEmpty(token)) {
                return Result<bool, string>.Err("Empty token");
            }
            return Result<bool, string>.Ok(true);
        }
    }
}
