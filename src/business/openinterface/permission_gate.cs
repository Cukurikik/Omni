using System;
using System.Collections.Generic;

namespace Omni.Business.OpenInterface
{
    public class OmniResult<T>
    {
        public T Data { get; }
        public string Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T data) { Data = data; }
        public OmniResult(string error) { Error = error; }
    }

    public class PermissionGate
    {
        private readonly HashSet<string> _restrictedCommands;

        public PermissionGate()
        {
            _restrictedCommands = new HashSet<string> { "fs_unlink", "sys_reboot", "proc_kill" };
        }

        public OmniResult<bool> AuthorizeAction(string cmdName, string userRole)
        {
            if (string.IsNullOrEmpty(cmdName) || string.IsNullOrEmpty(userRole))
            {
                return new OmniResult<bool>("Command and role must be specified.");
            }

            if (_restrictedCommands.Contains(cmdName))
            {
                if (userRole != "ADMIN" && userRole != "ROOT")
                {
                    return new OmniResult<bool>($"Access denied for {userRole} to execute {cmdName}");
                }
            }

            // Generate deterministic cryptographic audit token
            string auditToken = GenerateAuditToken(cmdName, userRole);
            return new OmniResult<bool>(true);
        }

        private string GenerateAuditToken(string cmd, string role)
        {
            var bytes = System.Text.Encoding.UTF8.GetBytes($"{cmd}-{role}-{DateTime.UtcNow.Ticks}");
            using (var sha = System.Security.Cryptography.SHA256.Create())
            {
                var hash = sha.ComputeHash(bytes);
                return Convert.ToBase64String(hash);
            }
        }
    }
}
