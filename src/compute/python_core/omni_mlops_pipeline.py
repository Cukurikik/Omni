from typing import List, Dict

class OmniMLOpsPipeline:
    """OMNI Compute Layer: MLOps Pipeline Manager (Zero-Mock)"""
    
    def __init__(self, max_concurrent: int):
        self.max_concurrent = max_concurrent

    def schedule_tasks(self, tasks: List[Dict[str, Any]]) -> List[str]:
        if not tasks:
            return []
            
        scheduled = []
        active = 0
        
        # Sort deterministically by priority
        sorted_tasks = sorted(tasks, key=lambda x: x.get('priority', 0), reverse=True)
        
        for task in sorted_tasks:
            if active < self.max_concurrent:
                scheduled.append(task['id'])
                active += 1
                
        return scheduled
