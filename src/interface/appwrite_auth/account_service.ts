import { Result, Ok, Err } from "@omni/core";

export class AccountService {
    public createSession(userId: string): Result<string, Error> {
        if (!userId) return Err(new Error("Missing user ID"));
        return Ok("session_token_123");
    }
}
