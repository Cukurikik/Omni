// omni_rbac_evaluator.rs — Role Based Access Control
// Layer: Domain / Rust
//
// Fast memory-safe RBAC engine for evaluating user permissions against
// OMNI Framework's strictly typed policies. Zero mock.

use std::collections::{HashMap, HashSet};

#[derive(Debug, Clone, Hash, Eq, PartialEq)]
pub struct Permission {
    pub resource: String,
    pub action: String,
}

#[derive(Debug, Clone)]
pub struct Role {
    pub name: String,
    pub permissions: HashSet<Permission>,
}

pub struct OmniRBACEvaluator {
    roles: HashMap<String, Role>,
    user_roles: HashMap<String, HashSet<String>>, // User ID -> Role Names
}

impl OmniRBACEvaluator {
    pub fn new() -> Self {
        OmniRBACEvaluator {
            roles: HashMap::new(),
            user_roles: HashMap::new(),
        }
    }

    /// Registers a new role with a specific set of permissions.
    pub fn add_role(&mut self, name: &str, permissions: Vec<Permission>) {
        let mut perm_set = HashSet::new();
        for p in permissions {
            perm_set.insert(p);
        }
        
        self.roles.insert(
            name.to_string(),
            Role {
                name: name.to_string(),
                permissions: perm_set,
            },
        );
    }

    /// Assigns a role to a specific user.
    pub fn assign_role_to_user(&mut self, user_id: &str, role_name: &str) -> Result<(), &'static str> {
        if !self.roles.contains_key(role_name) {
            return Err("Role does not exist");
        }

        let entry = self.user_roles.entry(user_id.to_string()).or_insert_with(HashSet::new);
        entry.insert(role_name.to_string());
        
        Ok(())
    }

    /// Revokes a role from a specific user.
    pub fn revoke_role_from_user(&mut self, user_id: &str, role_name: &str) {
        if let Some(roles) = self.user_roles.get_mut(user_id) {
            roles.remove(role_name);
        }
    }

    /// Evaluates whether a user has permission to perform an action on a resource.
    /// Supports wildcard '*' for actions.
    pub fn can_access(&self, user_id: &str, resource: &str, action: &str) -> bool {
        if let Some(roles) = self.user_roles.get(user_id) {
            for role_name in roles {
                if let Some(role) = self.roles.get(role_name) {
                    
                    // Exact match check
                    let exact_perm = Permission {
                        resource: resource.to_string(),
                        action: action.to_string(),
                    };
                    if role.permissions.contains(&exact_perm) {
                        return true;
                    }
                    
                    // Wildcard check
                    let wildcard_perm = Permission {
                        resource: resource.to_string(),
                        action: "*".to_string(),
                    };
                    if role.permissions.contains(&wildcard_perm) {
                        return true;
                    }
                }
            }
        }
        false
    }
}
