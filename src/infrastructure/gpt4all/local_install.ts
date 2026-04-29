import * as pulumi from "@pulumi/pulumi";
import * as local from "@pulumi/command/local";

// OMNI GPT4ALL: Edge Local Installation
// Pulumi script simulating the local deployment of a GPT4All environment on an edge device.
// This executes local commands to download the executable and the quantized GGUF weights.
// Source: nomic-ai/gpt4all

const config = new pulumi.Config();
const installDir = config.get("installDir") || "/opt/omni-gpt4all";
const modelUrl = "https://gpt4all.io/models/gguf/mistral-7b-instruct-v0.1.Q4_0.gguf";

// 1. Create Installation Directory
const createDir = new local.Command("create-install-dir", {
    create: `mkdir -p ${installDir}/models`,
    delete: `rm -rf ${installDir}`,
});

// 2. Download the Quantized Model (GGUF Format)
const downloadModel = new local.Command("download-model", {
    create: `curl -L ${modelUrl} -o ${installDir}/models/mistral-7b.gguf`,
    delete: `rm -f ${installDir}/models/mistral-7b.gguf`,
}, { dependsOn: createDir });

// 3. Write a configuration file for the edge runner
const writeConfig = new local.Command("write-config", {
    create: `cat <<EOF > ${installDir}/config.json
{
    "model_path": "${installDir}/models/mistral-7b.gguf",
    "threads": 4,
    "context_size": 4096
}
EOF`,
    delete: `rm -f ${installDir}/config.json`,
}, { dependsOn: createDir });

export const localInstallationPath = installDir;
