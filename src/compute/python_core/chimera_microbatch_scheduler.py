from typing import Dict, Any, List

class MicrobatchScheduler:
    def __init__(self, num_devices: int):
        self.num_devices = num_devices

    def get_device_map(self, num_layers: int) -> Dict[str, Any]:
        try:
            mapping = {i: i % self.num_devices for i in range(num_layers)}
            return {"status": "success", "device_map": mapping}
        except Exception as e:
            return {"status": "error", "message": str(e)}
