import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

// OMNI TF-SPARK: YARN Deployment
// Pulumi TS script simulating the provisioning of an EMR cluster to run Apache Spark and TensorFlowOnSpark.
// Source: yahoo/TensorFlowOnSpark

const config = new pulumi.Config();
const clusterName = "omni-tfspark-emr";

// EMR Role
const emrRole = new aws.iam.Role(`${clusterName}-role`, {
    assumeRolePolicy: JSON.stringify({
        Version: "2012-10-17",
        Statement: [{
            Action: "sts:AssumeRole",
            Principal: { Service: "elasticmapreduce.amazonaws.com" },
            Effect: "Allow",
        }],
    }),
});

// Create an EMR Cluster configured for Spark
const emrCluster = new aws.emr.Cluster(`${clusterName}-cluster`, {
    releaseLabel: "emr-6.10.0", // Contains Spark 3.x
    applications: ["Hadoop", "Spark"],
    serviceRole: emrRole.name,
    masterInstanceGroup: {
        instanceType: "m5.xlarge",
        instanceCount: 1,
    },
    coreInstanceGroup: {
        instanceType: "g4dn.2xlarge", // GPU instances for TF workers
        instanceCount: 4,
    },
    bootstrapActions: [
        {
            name: "install_tfonspark",
            // Script that installs pip packages: tensorflow, tensorflowonspark
            path: "s3://omni-scripts/install_tfonspark.sh", 
        }
    ],
    // Ensure Spark executors have GPU scheduling enabled
    configurationsJson: JSON.stringify([
        {
            Classification: "spark-defaults",
            Properties: {
                "spark.executor.resource.gpu.amount": "1",
                "spark.task.resource.gpu.amount": "1"
            }
        }
    ])
});

export const emrClusterId = emrCluster.id;
export const masterDns = emrCluster.masterPublicDns;
