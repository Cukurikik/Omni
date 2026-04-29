import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

/**
 * Omni Pulumi Infrastructure Core
 * Deterministic S3 and HPC Compute definition for K2 Geoscience.
 */

export const createK2Infra = () => {
    const k2Bucket = new aws.s3.Bucket("omni-k2-geoscience-data", {
        acl: "private",
        versioning: {
            enabled: true,
        },
    });

    const computeRole = new aws.iam.Role("omni-k2-hpc-role", {
        assumeRolePolicy: JSON.stringify({
            Version: "2012-10-17",
            Statement: [{
                Action: "sts:AssumeRole",
                Principal: {
                    Service: "ec2.amazonaws.com",
                },
                Effect: "Allow",
            }],
        }),
    });

    return {
        bucketName: k2Bucket.id,
        roleArn: computeRole.arn
    };
};
