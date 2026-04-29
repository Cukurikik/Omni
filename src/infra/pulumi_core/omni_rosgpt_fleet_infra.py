# Omni ROSGPT Robot Fleet Infra (Pulumi)
# Ref: bilel-bj/ROSGPT_Vision
import pulumi
import pulumi_aws as aws

robot_fleet_queue = aws.sqs.Queue("omni-rosgpt-command-queue",
    name="omni-rosgpt-commands",
    visibility_timeout_seconds=30,
    message_retention_seconds=3600,
    tags={"Project": "OMNI", "Batch": "22", "Engine": "ROSGPT"})

pulumi.export("command_queue_url", robot_fleet_queue.url)
