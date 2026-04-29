# Omni INTERS Search Index Infra (Pulumi)
# Ref: DaoD/INTERS — MIT
import pulumi
import pulumi_aws as aws

search_index_bucket = aws.s3.Bucket("omni-inters-search-index",
    bucket="omni-inters-search-indices",
    tags={"Project": "OMNI", "Batch": "23", "Engine": "INTERS"})

eval_queue = aws.sqs.Queue("omni-inters-eval-queue",
    name="omni-inters-evaluation",
    visibility_timeout_seconds=60,
    tags={"Project": "OMNI", "Engine": "INTERS"})

pulumi.export("search_index_bucket", search_index_bucket.bucket)
pulumi.export("eval_queue_url", eval_queue.url)
