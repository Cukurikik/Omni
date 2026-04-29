using Omni.Core;
namespace Omni.Keycloak { public class RoleMapper { public Result<bool, Error> Assign(string role) { return Result<bool, Error>.Ok(true); } } }