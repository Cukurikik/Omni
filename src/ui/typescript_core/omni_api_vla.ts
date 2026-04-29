export interface VLACommand {
    imageRef: string;
    instruction: string;
}

export class OmniVLAAPI {
    /** OMNI Interface Layer: VLA API */
    public static sendCommand(cmd: VLACommand): string {
        return `Executing "${cmd.instruction}" on ${cmd.imageRef}`;
    }
}
