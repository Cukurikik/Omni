using System;
using System.Collections.Generic;
using System.Linq;

namespace Omni.Domain.MoE
{
    // OMNI MOTHER Production Zero-Mock RBAC Policy Engine
    // Domain Driven Design entity restricting API access to specific MoE models
    // based on tenant roles and permissions.

    public enum MoERole
    {
        Guest,
        Developer,
        Enterprise,
        Admin
    }

    public enum MoEAction
    {
        Inference,
        FineTune,
        ExtractWeights,
        ConfigureRouter
    }

    public class RbacPolicy
    {
        public string ResourceId { get; }
        private readonly Dictionary<MoERole, HashSet<MoEAction>> _permissions;

        public RbacPolicy(string resourceId)
        {
            ResourceId = resourceId;
            _permissions = new Dictionary<MoERole, HashSet<MoEAction>>();
            foreach (MoERole role in Enum.GetValues(typeof(MoERole)))
            {
                _permissions[role] = new HashSet<MoEAction>();
            }
        }

        public void Grant(MoERole role, MoEAction action)
        {
            _permissions[role].Add(action);
        }

        public void Revoke(MoERole role, MoEAction action)
        {
            _permissions[role].Remove(action);
        }

        public bool CanExecute(MoERole role, MoEAction action)
        {
            // Admins can do anything
            if (role == MoERole.Admin) return true;

            return _permissions[role].Contains(action);
        }
    }

    public class RbacEngine
    {
        private readonly Dictionary<string, RbacPolicy> _policies = new();

        public RbacPolicy CreatePolicy(string resourceId)
        {
            var policy = new RbacPolicy(resourceId);
            _policies[resourceId] = policy;
            return policy;
        }

        public bool CheckAccess(string resourceId, MoERole role, MoEAction action)
        {
            if (_policies.TryGetValue(resourceId, out var policy))
            {
                return policy.CanExecute(role, action);
            }
            // Deny by default
            Console.WriteLine($"OMNI SECURE: Access Denied to {resourceId} for {role} attempting {action}");
            return false;
        }
    }
}
