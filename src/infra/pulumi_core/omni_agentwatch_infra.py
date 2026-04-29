# Omni AgentWatch Telemetry Infra (Pulumi)
# Ref: cyberark/agentwatch
import pulumi
import pulumi_aws as aws

telemetry_table = aws.dynamodb.Table("omni-agentwatch-events",
    name="omni-agentwatch-events",
    billing_mode="PAY_PER_REQUEST",
    hash_key="agent_id",
    range_key="timestamp",
    attributes=[
        aws.dynamodb.TableAttributeArgs(name="agent_id", type="S"),
        aws.dynamodb.TableAttributeArgs(name="timestamp", type="N"),
    ],
    tags={"Project": "OMNI", "Batch": "21", "Engine": "AgentWatch"})

pulumi.export("table_arn", telemetry_table.arn)
