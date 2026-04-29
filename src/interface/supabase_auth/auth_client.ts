import { Result, Ok, Err } from "@omni/core";

export class AuthClient {
    public signIn(email: string): Result<boolean, Error> {
        if (!email.includes("@")) {
            return Err(new Error("Invalid email"));
        }
        return Ok(true);
    }
}
