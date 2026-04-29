import { Result, Ok, Err } from "@omni/core";

export class RealtimeChannel {
    public subscribe(topic: string): Result<boolean, Error> {
        if (!topic) return Err(new Error("Topic empty"));
        return Ok(true);
    }
}
