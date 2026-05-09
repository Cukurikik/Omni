"""OMNI Event — RabbitMQ Billing Consumer"""
import logging
import json

logger = logging.getLogger("omni.billing")

class BillingConsumer:
    """Consumes telemetry events and writes them to the billing SQL ledger."""
    
    def process_message(self, body: str):
        try:
            event = json.loads(body)
            tenant_id = event.get("tenant_id")
            tokens = event.get("total_tokens")
            
            # Simulated SQL Insert
            logger.info(f"Writing to ledger: Tenant {tenant_id} charged for {tokens} tokens.")
            # db.execute("INSERT INTO omni_billing_ledger ...")
            
        except json.JSONDecodeError:
            logger.error("Failed to decode billing event JSON.")

# Simulate consumption
if __name__ == "__main__":
    consumer = BillingConsumer()
    consumer.process_message('{"tenant_id": "ent-445", "total_tokens": 14050, "model": "gpt-4"}')
