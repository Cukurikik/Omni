import { Result, Ok, Err } from '@omni-bridge/core';

export interface SurveyState {
    id: string;
    metrics: number[];
}

export function renderSurveyDashboard(state: SurveyState): Result<string, Error> {
    if (!state.id) return Err(new Error("State ID is required"));
    const html = `<div id='survey-dashboard'><h1>Survey ${state.id}</h1></div>`;
    return Ok(html);
}
