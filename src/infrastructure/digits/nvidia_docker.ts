import * as pulumi from "@pulumi/pulumi";
import * as docker from "@pulumi/docker";

// OMNI DIGITS: NVIDIA Docker Container Orchestration
// Launches the DIGITS web interface with GPU passthrough capabilities.
// Source: NVIDIA/DIGITS

const config = new pulumi.Config();
const digitsPort = config.getNumber("digitsPort") || 5000;
const hostDataPath = config.get("hostDataPath") || "/var/lib/omni/digits/data";
const hostJobsPath = config.get("hostJobsPath") || "/var/lib/omni/digits/jobs";

// Pull the NVIDIA DIGITS image
const digitsImage = new docker.RemoteImage("nvidia-digits-image", {
    name: "nvidia/digits:latest",
});

// Run the container
const digitsContainer = new docker.Container("nvidia-digits", {
    image: digitsImage.repoDigest,
    name: "omni-digits-ui",
    ports: [{
        internal: 5000,
        external: digitsPort,
    }],
    volumes: [
        {
            hostPath: hostDataPath,
            containerPath: "/data",
        },
        {
            hostPath: hostJobsPath,
            containerPath: "/workspace/jobs",
        }
    ],
    // Equivalent to --gpus all in Docker CLI for GPU access
    gpus: "all", 
    
    // Environment configurations
    envs: [
        "DIGITS_JOBS_DIR=/workspace/jobs",
        "DIGITS_LOGFILE_FILENAME=/workspace/jobs/digits.log"
    ],
    
    restart: "always",
});

export const url = pulumi.interpolate`http://localhost:${digitsPort}`;
