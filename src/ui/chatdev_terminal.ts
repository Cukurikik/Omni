import { Result, Ok, Err } from '@omni-bridge/core';

export function renderTerminal(logs: string[]): Result<boolean, Error> {
    if (!logs) return Err(new Error("No logs"));
    return Ok(true);
}
