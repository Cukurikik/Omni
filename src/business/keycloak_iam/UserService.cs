using Omni.Core;

namespace KeycloakIam {
    public class UserService {
        public Result<string, string> GetUserId(string username) {
            if (string.IsNullOrEmpty(username)) return Result<string, string>.Err("Invalid user");
            return Result<string, string>.Ok("uid-123");
        }
    }
}
