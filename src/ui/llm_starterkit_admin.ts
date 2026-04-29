import { Result, Ok, Err } from '@omni-bridge/core';

export function renderStarterAdmin(user: string): Result<string, Error> {
    if (!user) return Err(new Error("User missing"));
    return Ok(`<h1>Admin: ${user}</h1>`);
}
