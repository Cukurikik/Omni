// OMNI Infrastructure — Pulumi Azure AKS Provisioning
import * as pulumi from "@pulumi/pulumi";
import * as azure_native from "@pulumi/azure-native";

// Create an Azure Resource Group
const resourceGroup = new azure_native.resources.ResourceGroup("omniResourceGroup", {
    location: "EastUS",
});

// Create an AKS cluster for OMNI workloads
const cluster = new azure_native.containerservice.ManagedCluster("omniAKSCluster", {
    resourceGroupName: resourceGroup.name,
    location: resourceGroup.location,
    agentPoolProfiles: [{
        count: 3,
        maxPods: 110,
        mode: "System",
        name: "agentpool",
        osDiskSizeGB: 100,
        osType: "Linux",
        vmSize: "Standard_NC6s_v3", // GPU enabled VM type
    }],
    dnsPrefix: "omni-aks",
    enableRBAC: true,
    kubernetesVersion: "1.27.3",
    linuxProfile: {
        adminUsername: "omniadmin",
        ssh: {
            publicKeys: [{
                keyData: "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC...", // Placeholder
            }],
        },
    },
});

export const kubeconfig = cluster.kubeConfig;
