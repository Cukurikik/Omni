# Omni Advanced RAG Infra (Pulumi)
# Ref: GURPREETKAURJETHRA/Advanced_RAG
import pulumi
import pulumi_aws as aws

rag_queue = aws.sqs.Queue("omni-rag-query-queue",
    name="omni-advanced-rag-queries",
    visibility_timeout_seconds=120,
    message_retention_seconds=86400,
    tags={"Project": "OMNI", "Batch": "22", "Engine": "AdvancedRAG"})

pulumi.export("queue_url", rag_queue.url)
