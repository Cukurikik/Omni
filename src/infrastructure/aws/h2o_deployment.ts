import * as aws from "@pulumi/aws";

const h2oInstance = new aws.ec2.Instance("h2o-node", {
    ami: "ami-0c55b159cbfafe1f0",
    instanceType: "m5.4xlarge", // High memory for H2O
    tags: {
        Name: "H2O-Distributed-Node",
    },
});
