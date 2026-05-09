import * as gcp from "@pulumi/gcp";

// OMNI MOTHER: Pulumi Infrastructure for GCP A3 VMs (H100)

const pikvInstance = new gcp.compute.Instance("omni-pikv-node", {
    machineType: "a3-highgpu-8g",
    zone: "us-central1-a",
    bootDisk: {
        initializeParams: { image: "deeplearning-platform-release/common-cu121" },
    },
    networkInterfaces: [{
        network: "default",
        accessConfigs: [{}],
    }],
    guestAccelerators: [{
        type: "nvidia-h100-80gb",
        count: 8,
    }],
});
