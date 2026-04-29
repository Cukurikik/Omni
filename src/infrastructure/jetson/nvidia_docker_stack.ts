import * as pulumi from "@pulumi/pulumi";
import * as docker from "@pulumi/docker";

// OMNI Infrastructure Layer: NVIDIA Jetson Docker Stack
// Deploys L4T ML containers for edge inference on Jetson devices.

export class JetsonInferenceNode extends pulumi.ComponentResource {
    public readonly containerId: pulumi.Output<string>;

    constructor(name: string, deviceIp: string, opts?: pulumi.ComponentResourceOptions) {
        super("omni:edge:JetsonNode", name, {}, opts);

        // Assume Pulumi is executing this against a remote Docker daemon on the Jetson device
        const provider = new docker.Provider(`${name}-docker-provider`, {
            host: `tcp://${deviceIp}:2375`,
        });

        // Pull the L4T PyTorch image
        const l4tImage = new docker.RemoteImage(`${name}-l4t-pytorch`, {
            name: "nvcr.io/nvidia/l4t-pytorch:r35.2.1-pth2.0-py3",
        }, { provider, parent: this });

        // Deploy the ExecuTorch / Tengine Edge runtime container
        const inferenceContainer = new docker.Container(`${name}-inference-runtime`, {
            image: l4tImage.name,
            name: `omni-edge-${name}`,
            restart: "always",
            gpus: "all", // Enable NVIDIA GPU passthrough for Jetson
            ports: [{
                internal: 8080,
                external: 8080,
            }],
            envs: [
                "OMNI_EDGE_NODE_ID=jetson-alpha-1",
                "OMNI_RUNTIME=executorch"
            ],
            // Mount volume for local model caching
            volumes: [{
                hostPath: "/var/omni/models",
                containerPath: "/models",
            }]
        }, { provider, parent: this });

        this.containerId = inferenceContainer.id;

        this.registerOutputs({
            containerId: this.containerId,
        });
    }
}
