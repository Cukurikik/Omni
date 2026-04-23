import datetime
from typing import Any, Dict, List, Set, Optional
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniFirebaseRBACEngine:
    """
    OmniFirebaseRBACEngine
    Batch: 26 (Semester 10)
    Source: jamezmca/react-firebase-auth-db-template
    
    A zero-mock engine for resolving Role-Based Access Control (RBAC) graphs.
    Computes effective inherited roles via BFS and evaluates access 
    against specific resource ACL rules.
    """
    
    def __init__(self, role_hierarchy: Dict[str, List[str]], resource_rules: Dict[str, Dict[str, List[str]]]):
        """
        :param role_hierarchy: Mapping from a role to the list of roles it implicitly inherits.
                               Example: {"admin": ["editor"], "editor": ["viewer"]}
        :param resource_rules: Mapping from resource to action to required roles.
                               Example: {"reports": {"write": ["editor"], "read": ["viewer"]}}
        """
        self.role_hierarchy = role_hierarchy
        self.resource_rules = resource_rules

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": self.__class__.__name__,
            "status": "operational",
            "roles_configured": list(self.role_hierarchy.keys()),
            "resources_configured": list(self.resource_rules.keys()),
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
        
    def resolve_effective_roles(self, user_base_roles: List[str]) -> Result[Set[str], Exception]:
        """
        Resolves the full set of effective roles using BFS traversal over the hierarchy graph.
        """
        try:
            if not isinstance(user_base_roles, list):
                return Err(ValueError("user_base_roles must be a list"))
                
            effective_roles: Set[str] = set()
            queue: List[str] = list(user_base_roles)
            
            # BFS to find all inherited roles
            while queue:
                current_role = queue.pop(0)
                if current_role not in effective_roles:
                    effective_roles.add(current_role)
                    if current_role in self.role_hierarchy:
                        queue.extend(self.role_hierarchy[current_role])
                        
            return Ok(effective_roles)
        except Exception as e:
            return Err(e)

    def evaluate_access(self, user_base_roles: List[str], resource: str, action: str) -> Result[bool, Exception]:
        """
        Evaluates whether a user with given base roles has access to the specified resource/action.
        """
        try:
            if resource not in self.resource_rules:
                return Err(KeyError(f"Resource '{resource}' is not defined in rules"))
                
            if action not in self.resource_rules[resource]:
                return Err(KeyError(f"Action '{action}' is not defined for resource '{resource}'"))
                
            required_roles = self.resource_rules[resource][action]
            
            roles_result = self.resolve_effective_roles(user_base_roles)
            if not roles_result.is_ok():
                return roles_result
                
            effective_roles = roles_result.unwrap()
            
            # Check intersection
            has_access = any(role in effective_roles for role in required_roles)
            return Ok(has_access)
            
        except Exception as e:
            return Err(e)

    def generate_access_matrix(self, user_base_roles: List[str]) -> Result[Dict[str, Dict[str, bool]], Exception]:
        """
        Generates a comprehensive matrix of allowed/denied actions for every resource for a given user.
        """
        try:
            matrix: Dict[str, Dict[str, bool]] = {}
            for resource, actions in self.resource_rules.items():
                matrix[resource] = {}
                for action in actions.keys():
                    access_val = self.evaluate_access(user_base_roles, resource, action).unwrap()
                    matrix[resource][action] = access_val
            return Ok(matrix)
            
        except Exception as e:
            return Err(e)
