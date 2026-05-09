# OMNI Framework - Celery Task Broker (Python)
# Configures Celery to use RabbitMQ for asynchronous offline AI tasks (e.g., dataset generation)

from celery import Celery
import os

broker_url = os.environ.get("OMNI_RABBITMQ_URL", "amqp://guest:guest@localhost:5672//")
backend_url = os.environ.get("OMNI_REDIS_URL", "redis://localhost:6379/1")

app = Celery('omni_tasks', broker=broker_url, backend=backend_url)

app.conf.update(
    task_serializer='json',
    accept_content=['json'],  # Ignore other content
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_routes={
        'omni.tasks.train.*': {'queue': 'training'},
        'omni.tasks.inference.*': {'queue': 'inference'},
    }
)

@app.task(name="omni.tasks.inference.batch_generate")
def async_batch_generate(prompts: list):
    """
    Offline batch generation task.
    """
    print(f"OMNI Celery: Processing {len(prompts)} prompts in batch...")
    # Inference logic here
    return {"status": "completed", "processed": len(prompts)}
