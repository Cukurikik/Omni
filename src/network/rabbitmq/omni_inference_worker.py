"""
OMNI Event Layer — RabbitMQ Inference Event Worker
Async inference job consumer with dead-letter handling.
"""
import json, time, logging, uuid
from dataclasses import dataclass, asdict
from typing import Optional, Callable

logger = logging.getLogger("omni.rabbitmq")

@dataclass
class InferenceJob:
    job_id: str; prompt: str; model_id: str = "omni-7b"
    max_tokens: int = 256; temperature: float = 0.7; priority: int = 0
    created_at: float = 0.0
    def __post_init__(self):
        if not self.created_at: self.created_at = time.time()

@dataclass
class InferenceResult:
    job_id: str; text: str; tokens: int; latency_ms: float; status: str = "completed"

class OmniRabbitMQWorker:
    """RabbitMQ consumer for inference job processing."""

    QUEUE_INFER = "omni.inference.jobs"
    QUEUE_RESULTS = "omni.inference.results"
    QUEUE_DLX = "omni.inference.dead-letter"
    EXCHANGE = "omni.inference"

    def __init__(self, amqp_url: str = "amqp://guest:guest@localhost:5672/",
                 inference_fn: Optional[Callable] = None, prefetch: int = 1):
        self.amqp_url = amqp_url
        self.inference_fn = inference_fn or self._default_inference
        self.prefetch = prefetch
        self.stats = {"processed": 0, "errors": 0, "total_latency": 0.0}

    def setup_topology(self, channel):
        """Declare exchanges, queues, and bindings."""
        channel.exchange_declare(exchange=self.EXCHANGE, exchange_type="topic", durable=True)
        # Dead letter exchange
        channel.exchange_declare(exchange=f"{self.EXCHANGE}.dlx", exchange_type="fanout", durable=True)
        channel.queue_declare(queue=self.QUEUE_DLX, durable=True)
        channel.queue_bind(queue=self.QUEUE_DLX, exchange=f"{self.EXCHANGE}.dlx")
        # Main queue with DLX
        channel.queue_declare(queue=self.QUEUE_INFER, durable=True, arguments={
            "x-dead-letter-exchange": f"{self.EXCHANGE}.dlx",
            "x-message-ttl": 300000,  # 5 min TTL
            "x-max-length": 10000,
        })
        channel.queue_bind(queue=self.QUEUE_INFER, exchange=self.EXCHANGE, routing_key="infer.#")
        # Results queue
        channel.queue_declare(queue=self.QUEUE_RESULTS, durable=True)
        channel.queue_bind(queue=self.QUEUE_RESULTS, exchange=self.EXCHANGE, routing_key="result.#")
        channel.basic_qos(prefetch_count=self.prefetch)

    def process_message(self, ch, method, properties, body):
        """Process a single inference job."""
        start = time.time()
        try:
            data = json.loads(body)
            job = InferenceJob(**data)
            text = self.inference_fn(job)
            latency = (time.time() - start) * 1000

            result = InferenceResult(job_id=job.job_id, text=text,
                                     tokens=len(text.split()), latency_ms=round(latency, 2))

            ch.basic_publish(exchange=self.EXCHANGE, routing_key="result.completed",
                           body=json.dumps(asdict(result)),
                           properties=self._persistent_props())

            self.stats["processed"] += 1
            self.stats["total_latency"] += latency
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f"Job {job.job_id} completed in {latency:.1f}ms")

        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"Job failed: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)  # Send to DLX

    def _default_inference(self, job: InferenceJob) -> str:
        return f"Response for: {job.prompt[:80]}"

    def _persistent_props(self):
        import pika
        return pika.BasicProperties(delivery_mode=2, content_type="application/json")

    def start(self):
        """Connect and start consuming."""
        import pika
        connection = pika.BlockingConnection(pika.URLParameters(self.amqp_url))
        channel = connection.channel()
        self.setup_topology(channel)
        channel.basic_consume(queue=self.QUEUE_INFER, on_message_callback=self.process_message)
        logger.info(f"RabbitMQ worker started on {self.QUEUE_INFER}")
        channel.start_consuming()

    def get_stats(self) -> dict:
        avg = self.stats["total_latency"] / max(self.stats["processed"], 1)
        return {**self.stats, "avg_latency_ms": round(avg, 2)}

if __name__ == "__main__":
    worker = OmniRabbitMQWorker()
    worker.start()
