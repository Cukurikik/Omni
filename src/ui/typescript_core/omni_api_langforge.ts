// Omni API for Langforge Deployment Manifest
export interface DeploymentManifest {
    appName: string;
    targetPlatform: string;
    replicas: number;
}

export class OmniLangforgeAPI {
    static buildK8sManifest(config: DeploymentManifest): string {
        return `
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ${config.appName}
spec:
  replicas: ${config.replicas}
  selector:
    matchLabels:
      app: ${config.appName}
  template:
    metadata:
      labels:
        app: ${config.appName}
    spec:
      containers:
      - name: llm-engine
        image: omni/${config.targetPlatform}:latest
        `.trim();
    }
}
