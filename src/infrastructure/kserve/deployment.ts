import * as k8s from "@pulumi/kubernetes";

// KServe InferenceService definition via Pulumi
export const modelServing = new k8s.apiextensions.CustomResource("sklearn-iris", {
    apiVersion: "serving.kserve.io/v1beta1",
    kind: "InferenceService",
    metadata: {
        name: "sklearn-iris",
        namespace: "kserve-test",
    },
    spec: {
        predictor: {
            sklearn: {
                storageUri: "gs://kfserving-examples/models/sklearn/1.0/model",
            }
        }
    }
});
