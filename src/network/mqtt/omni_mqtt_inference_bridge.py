# OMNI Event Layer — MQTT IoT Inference Bridge
# MQTT client for edge device inference on IoT networks.

import paho.mqtt.client as mqtt
import json
import uuid
import time
import logging
from dataclasses import dataclass, asdict
from typing import Optional, Callable

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("omni.mqtt")


@dataclass
class InferenceRequest:
    """MQTT inference request payload."""
    device_id: str
    prompt: str
    max_tokens: int = 128
    temperature: float = 0.7
    request_id: str = ""

    def __post_init__(self):
        if not self.request_id:
            self.request_id = str(uuid.uuid4())


@dataclass
class InferenceResponse:
    """MQTT inference response payload."""
    request_id: str
    device_id: str
    generated_text: str
    tokens_generated: int
    latency_ms: float
    finish_reason: str = "stop"


class OmniMQTTBridge:
    """MQTT bridge for edge device transformer inference."""

    TOPIC_REQUEST = "omni/inference/request"
    TOPIC_RESPONSE = "omni/inference/response/{device_id}"
    TOPIC_HEALTH = "omni/inference/health"
    TOPIC_METRICS = "omni/inference/metrics"

    def __init__(
        self,
        broker_host: str = "localhost",
        broker_port: int = 1883,
        client_id: str = "omni-inference-bridge",
        inference_fn: Optional[Callable] = None,
    ):
        self.client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv5)
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.inference_fn = inference_fn or self._default_inference
        self.stats = {"total": 0, "errors": 0, "total_latency": 0.0}

        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.will_set(self.TOPIC_HEALTH, json.dumps({"status": "offline"}), qos=1, retain=True)

    def start(self):
        """Connect and start the MQTT bridge."""
        self.client.connect(self.broker_host, self.broker_port, keepalive=60)
        logger.info(f"Connected to MQTT broker at {self.broker_host}:{self.broker_port}")
        self.client.loop_forever()

    def _on_connect(self, client, userdata, flags, rc, properties=None):
        logger.info("MQTT connected, subscribing to inference requests")
        client.subscribe(self.TOPIC_REQUEST, qos=1)
        client.publish(
            self.TOPIC_HEALTH,
            json.dumps({"status": "online", "timestamp": time.time()}),
            qos=1, retain=True,
        )

    def _on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            request = InferenceRequest(**payload)
            start_time = time.time()

            result = self.inference_fn(request)
            latency = (time.time() - start_time) * 1000

            response = InferenceResponse(
                request_id=request.request_id,
                device_id=request.device_id,
                generated_text=result,
                tokens_generated=len(result.split()),
                latency_ms=round(latency, 2),
            )

            response_topic = self.TOPIC_RESPONSE.format(device_id=request.device_id)
            client.publish(response_topic, json.dumps(asdict(response)), qos=1)

            self.stats["total"] += 1
            self.stats["total_latency"] += latency
            self._publish_metrics()

        except Exception as e:
            logger.error(f"Inference error: {e}")
            self.stats["errors"] += 1

    def _default_inference(self, request: InferenceRequest) -> str:
        return f"Edge response for: {request.prompt[:80]}"

    def _publish_metrics(self):
        if self.stats["total"] % 10 == 0:
            avg_lat = self.stats["total_latency"] / max(self.stats["total"], 1)
            self.client.publish(
                self.TOPIC_METRICS,
                json.dumps({**self.stats, "avg_latency_ms": round(avg_lat, 2)}),
                qos=0,
            )


if __name__ == "__main__":
    bridge = OmniMQTTBridge(broker_host="localhost", broker_port=1883)
    bridge.start()
