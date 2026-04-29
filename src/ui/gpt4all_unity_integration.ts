import { Result, Ok, Err } from '@omni-bridge/core';

export function bridgeUI(command: string): Result<boolean, Error> {
    if (!command) return Err(new Error("Command missing"));
    return Ok(true);
}
