from typing import List, Dict, Optional, Tuple

# OMNI METAGPT: Role Planner
# Python domain logic for orchestrating Multi-Agent Software Company roles 
# (Product Manager, Architect, Engineer, QA).
# Source: geekan/MetaGPT

class PlannerError(Exception):
    pass

class Role:
    def __init__(self, name: str, profile: str, goal: str):
        self.name = name
        self.profile = profile
        self.goal = goal

class RolePlanner:
    """
    Given a user requirement, the Planner dynamically instantiates the required roles
    and sets up the workflow chain.
    """
    def __init__(self):
        self.roles: Dict[str, Role] = {}
        self._register_standard_roles()

    def _register_standard_roles(self):
        self.roles["PM"] = Role(
            "Alice", "Product Manager", "Write PRD and define user stories."
        )
        self.roles["Architect"] = Role(
            "Bob", "System Architect", "Design system architecture and API specs."
        )
        self.roles["Engineer"] = Role(
            "Charlie", "Software Engineer", "Write production code based on design."
        )
        self.roles["QA"] = Role(
            "Dave", "QA Engineer", "Write unit tests and find bugs."
        )

    def plan_workflow(self, requirement: str) -> Tuple[Optional[List[Role]], Optional[PlannerError]]:
        """
        Monadic return: Returns the sequence of roles to execute or an error.
        """
        if not requirement or len(requirement.strip()) < 10:
            return None, PlannerError("Requirement is too vague or short to plan a workflow.")

        # For a standard software project, the pipeline is sequential
        workflow = [
            self.roles["PM"],
            self.roles["Architect"],
            self.roles["Engineer"],
            self.roles["QA"]
        ]
        
        return workflow, None

    def execute_role(self, role: Role, context: str) -> str:
        """
        Simulates an LLM call for the specific role's action.
        """
        # In production, this invokes the LLM with the Role's system prompt and context.
        return f"[{role.profile} {role.name}] completed task based on context length {len(context)}."
