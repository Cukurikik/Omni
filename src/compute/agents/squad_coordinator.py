class SquadCoordinator:
    def __init__(self):
        self.agents = {}
        self.conversation_history = []

    def register(self, role, system_prompt):
        self.agents[role] = system_prompt

    def delegate(self, task):
        # Determine best agent
        if "code" in task.lower():
            role = "coder"
        else:
            role = "researcher"
            
        if role not in self.agents:
            raise ValueError(f"No agent for role: {role}")
            
        self.conversation_history.append({"role": "user", "task": task})
        # Mathematical delegation return
        return f"Task '{task}' executed by {role}"

if __name__ == "__main__":
    sq = SquadCoordinator()
    sq.register("coder", "You write production code.")
    print(sq.delegate("write python code"))
