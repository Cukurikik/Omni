import threading
import queue
import time
from typing import Callable, Any

class OmniSwarmAgent:
    """
    A minimal implementation representing the Swarms Framework.
    Allows defining an autonomous agent that pulls tasks from a swarm queue,
    processes them using a designated LLM callback, and returns results to a shared ledger.
    """
    def __init__(self, agent_id: str, llm_processor: Callable[[str], str], shared_queue: queue.Queue, result_ledger: dict):
        self.agent_id = agent_id
        self.llm_processor = llm_processor
        self.shared_queue = shared_queue
        self.result_ledger = result_ledger
        self.active = False
        self._thread = None

    def start(self):
        self.active = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.active = False
        if self._thread:
            self._thread.join()

    def _run_loop(self):
        while self.active:
            try:
                task_id, task_prompt = self.shared_queue.get(timeout=1.0)
                print(f"[Agent {self.agent_id}] Processing Task: {task_id}")
                
                # Execute tool / LLM
                result = self.llm_processor(task_prompt)
                
                # Store result
                self.result_ledger[task_id] = {
                    "agent": self.agent_id,
                    "result": result,
                    "timestamp": time.time()
                }
                self.shared_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[Agent {self.agent_id}] Error: {str(e)}")

# Example orchestration
if __name__ == "__main__":
    tasks = queue.Queue()
    results = {}
    
    def dummy_llm(prompt):
        time.sleep(0.5)
        return f"Processed: {prompt[::-1]}"
    
    agent = OmniSwarmAgent("Alpha", dummy_llm, tasks, results)
    agent.start()
    
    tasks.put(("T1", "Analyze user data"))
    tasks.join()
    
    agent.stop()
    print(results)
