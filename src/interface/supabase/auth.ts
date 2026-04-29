import { Result, Ok } from "@omni/core";

export function signIn(email: string): Result<boolean, Error> {
    return Ok(true);
}
