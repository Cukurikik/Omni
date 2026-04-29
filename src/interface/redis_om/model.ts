import { Result, Ok } from "@omni/core";

export class RedisModel {
    save(): Result<boolean, Error> {
        return Ok(true);
    }
}
