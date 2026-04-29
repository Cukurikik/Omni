import { Result, Ok, Err } from '@omni-bridge/core';

export function generateReport(score: number): Result<string, Error> {
    if (score < 0 || score > 1) return Err(new Error("Score out of bounds"));
    return Ok(`Report: Score is ${score}`);
}
