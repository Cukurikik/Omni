import datetime
from typing import Any, Dict, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniEscapeRoomStateEngine:
    """
    OmniEscapeRoomStateEngine
    Batch: 26 (Semester 10)
    Source: heedrox/ric-escape
    
    A zero-mock text adventure environment Finite State Machine.
    Validates inventory constraints, executes state transitions (e.g. using keys on doors),
    and deterministically mutates the inventory snapshot upon successful actions.
    """
    
    def __init__(self, state_graph: Dict[str, Dict[str, Any]]):
        """
        :param state_graph: Definition of rooms and actions.
        Example:
        {
            "cell": {
                "actions": {
                    "use_key_on_door": {
                        "requires": ["rusty_key"],
                        "consumes": ["rusty_key"],
                        "awards": ["hallway_map"],
                        "transitions_to": "hallway"
                    }
                }
            }
        }
        """
        self.state_graph = state_graph

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": self.__class__.__name__,
            "status": "operational",
            "mapped_states": list(self.state_graph.keys()),
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

    def evaluate_transition(
        self, current_room: str, action: str, current_inventory: List[str]
    ) -> Result[Dict[str, Any], Exception]:
        """
        Evaluate if an action is valid in the current room given the current_inventory.
        Returns the new state payload: {"new_room": str, "new_inventory": List[str]}
        """
        try:
            if current_room not in self.state_graph:
                return Err(KeyError(f"Room '{current_room}' does not exist in state graph"))
                
            room_def = self.state_graph[current_room]
            actions = room_def.get("actions", {})
            
            if action not in actions:
                return Err(KeyError(f"Action '{action}' does not exist in room '{current_room}'"))
                
            action_def = actions[action]
            
            requires = action_def.get("requires", [])
            consumes = action_def.get("consumes", [])
            awards = action_def.get("awards", [])
            target_room = action_def.get("transitions_to", current_room)
            
            # Check requirements
            inventory_copy = list(current_inventory)
            for req in requires:
                if req not in inventory_copy:
                    return Err(ValueError(f"Missing required item: '{req}'"))
                    
            # Consume items
            for cons in consumes:
                if cons in inventory_copy:
                    inventory_copy.remove(cons)
                    
            # Award items
            for award in awards:
                inventory_copy.append(award)
                
            return Ok({
                "new_room": target_room,
                "new_inventory": sorted(inventory_copy),
                "action_taken": action
            })
            
        except Exception as e:
            return Err(e)
