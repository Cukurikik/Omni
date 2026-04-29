import * as pulumi from "@pulumi/pulumi";
import * as kubernetes from "@pulumi/kubernetes";

// OMNI Infrastructure Layer: Seldon Kubernetes Operator
// Deploys the Seldon-Core CRDs and inference graphs using Pulumi.

export class SeldonDeployment extends pulumi.ComponentResource {
    public readonly endpointUrl: pulumi.Output<string>;

    constructor(name: string, namespace: string, modelUri: string, opts?: pulumi.ComponentResourceOptions) {
        super("omni:seldon:Deployment", name, {}, opts);

        // Define the SeldonDeployment Custom Resource
        const seldonDep = new kubernetes.apiextensions.CustomResource(name, {
            apiVersion: "machinelearning.seldon.io/v1",
            kind: "SeldonDeployment",
            metadata: {
                name: name,
                namespace: namespace,
            },
            spec: {
                name: `${name}-graph`,
                predictors: [{
                    componentSpecs: [{
                        spec: {
                            containers: [{
                                name: "classifier",
                                image: "seldonio/sklearnserver:1.15.0",
                                env: [
                                    { name: "MODEL_URI", value: modelUri }
                                ],
                                resources: {
                                    limits: { cpu: "2", memory: "4Gi" },
                                    requests: { cpu: "1", memory: "2Gi" }
                                }
                            }]
                        }
                    }],
                    graph: {
                        children: [],
                        endpoint: { type: "REST" },
                        name: "classifier",
                        type: "MODEL"
                    },
                    name: "default",
                    replicas: 2
                }]
            }
        }, { parent: this });

        // Assume Istio ingress gateway is routing to this Seldon Deployment
        this.endpointUrl = pulumi.interpolate`http://omni-gateway.${namespace}.svc.cluster.local/seldon/${namespace}/${name}/api/v1.0/predictions`;

        this.registerOutputs({
            endpointUrl: this.endpointUrl,
        });
    }
}
