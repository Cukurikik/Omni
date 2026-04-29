import { Result, Ok, Err } from '@omni-bridge/core';

export function renderEditor(code: string): Result<string, Error> {
    if (code === null) return Err(new Error("Code is null"));
    return Ok(`<div>${code}</div>`);
}
