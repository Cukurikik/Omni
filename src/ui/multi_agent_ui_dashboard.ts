import { Result, Ok, Err } from '@omni-bridge/core';

export function initializeAgentUI(agents: string[]): Result<boolean, Error> {
    if (agents.length === 0) return Err(new Error("No agents provided for UI"));
    return Ok(true);
}
