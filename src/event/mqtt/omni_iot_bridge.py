"""OMNI Event — MQTT IoT Edge Bridge"""
import logging
import json
import random
import time

logger = logging.getLogger("omni.mqtt")

class OmniIoTBridge:
    """
    Simulates an MQTT Bridge that collects inference requests from low-power 
    edge devices (like Raspberry Pi or microcontrollers) and routes them to the OMNI cluster.
    """
    def __init__(self, broker_url: str):
        self.broker_url = broker_url
        logger.info(f"Connected to MQTT Broker at {broker_url}")

    def on_message(self, topic: str, payload: str):
        """Callback when an edge device publishes sensor data requiring AI analysis."""
        data = json.loads(payload)
        device_id = data.get("device_id", "unknown")
        sensor_value = data.get("value", 0.0)
        
        logger.info(f"Received IoT event from {device_id} on {topic}: Value={sensor_value}")
        
        # Route to OMNI Model (mock)
        prediction = self._route_to_omni(sensor_value)
        
        # Publish response back to device
        self._publish(f"omni/devices/{device_id}/action", json.dumps({"action": prediction}))

    def _route_to_omni(self, value: float) -> str:
        """Mock routing to the LLM/ML cluster."""
        if value > 80.0:
            return "TRIGGER_COOLING"
        return "NORMAL_OPERATION"
        
    def _publish(self, topic: str, payload: str):
        logger.info(f"MQTT Publish -> {topic}: {payload}")

# Simulation
if __name__ == "__main__":
    bridge = OmniIoTBridge("tcp://mqtt.omni.internal:1883")
    bridge.on_message("omni/devices/temp_sensor_1/data", json.dumps({"device_id": "temp_sensor_1", "value": 85.5}))
