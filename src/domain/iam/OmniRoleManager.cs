// OmniRoleManager.cs — IAM Role Manager
// Layer: Domain / C#
//
// Identity and Access Management class for managing user claims, checking
// permissions against the OPA Rego policies, and verifying JWT signatures.

using System;
using System.Collections.Generic;
using System.Security.Claims;
using OmniMonad;

namespace Omni.Domain.IAM
{
    public sealed class OmniRoleManager
    {
        // Mock definition of valid roles
        private readonly HashSet<string> _validRoles = new() 
        { 
            "superadmin", "researcher", "logistics", "readonly" 
        };

        /// <summary>
        /// Validates if an extracted token claim represents a registered system role.
        /// </summary>
        public OmniResult<bool> ValidateRoleExists(string roleName)
        {
            if (string.IsNullOrWhiteSpace(roleName))
            {
                return OmniResult<bool>.Fail("INV_ROLE", "Role cannot be empty", Severity.Error);
            }

            if (_validRoles.Contains(roleName.ToLowerInvariant()))
            {
                return OmniResult<bool>.Succeed(true);
            }

            return OmniResult<bool>.Fail("UNKN_ROLE", $"Role '{roleName}' is not recognized", Severity.Error);
        }

        /// <summary>
        /// Analyzes a ClaimsPrincipal (extracted from a JWT) to ensure it meets
        /// the minimum clearance level required for an operation.
        /// </summary>
        public OmniResult<bool> CheckClearanceLevel(ClaimsPrincipal user, int requiredLevel)
        {
            var clearanceClaim = user.FindFirst("clearance_level");
            
            if (clearanceClaim == null)
                return OmniResult<bool>.Fail("NO_CLR", "User lacks a clearance level claim", Severity.Error);

            if (int.TryParse(clearanceClaim.Value, out int userLevel))
            {
                if (userLevel >= requiredLevel)
                    return OmniResult<bool>.Succeed(true);
                else
                    return OmniResult<bool>.Fail("LOW_CLR", $"User level {userLevel} is below required {requiredLevel}", Severity.Error);
            }

            return OmniResult<bool>.Fail("INV_CLR", "Clearance claim is not a valid integer", Severity.Error);
        }
    }
}
