import * as aws from "@pulumi/aws";

// Edge deployment simulation for EasyPR model serving
const easyprEdge = new aws.iot.Thing("easypr-camera-node", {
    attributes: {
        location: "entrance-gate-1",
        model_version: "v2.1",
    },
});
