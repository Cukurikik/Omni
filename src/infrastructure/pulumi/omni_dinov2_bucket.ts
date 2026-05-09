// OMNI Framework - Pulumi script for DINOv2 S3 Infrastructure
import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

// Create an AWS resource (S3 Bucket) for storing DINOv2 satellite datasets
const satelliteBucket = new aws.s3.Bucket("omni-dinov2-imagery", {
    acl: "private",
    versioning: {
        enabled: true,
    },
    serverSideEncryptionConfiguration: {
        rule: {
            applyServerSideEncryptionByDefault: {
                sseAlgorithm: "AES256",
            },
        },
    },
    tags: {
        Environment: "Production",
        Project: "OMNI-Framework",
        Layer: "Infrastructure",
    },
});

// Export the name of the bucket
export const bucketName = satelliteBucket.id;
