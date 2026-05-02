// @omni-domain Interface Layer (LLM Interview)
// @omni-source various/llm-interview
// @omni-description LLM Interview App mimicking Android frontend for interview scoring.
// @omni-requirement zero-mock, monadic-error

package com.omni.llminterview.app

class OmniResult<T>(val ok: Boolean, val value: T?, val error: Exception?) {
    companion object {
        fun <T> ok(value: T): OmniResult<T> = OmniResult(true, value, null)
        fun <T> err(error: Exception): OmniResult<T> = OmniResult(false, null, error)
    }
}

data class InterviewFeedback(val candidateId: String, val score: Int, val comments: String)

class LLMInterviewApp {
    private val feedbackDB = mutableMapOf<String, InterviewFeedback>()

    fun submitFeedback(candidateId: String, score: Int, comments: String): OmniResult<Boolean> {
        if (candidateId.isBlank()) {
            return OmniResult.err(IllegalArgumentException("Candidate ID cannot be empty"))
        }
        if (score !in 0..100) {
            return OmniResult.err(IllegalArgumentException("Score must be between 0 and 100"))
        }

        val feedback = InterviewFeedback(candidateId, score, comments)
        feedbackDB[candidateId] = feedback
        
        return OmniResult.ok(true)
    }

    fun viewFeedback(candidateId: String): OmniResult<InterviewFeedback> {
        val fb = feedbackDB[candidateId]
        return if (fb != null) {
            OmniResult.ok(fb)
        } else {
            OmniResult.err(NoSuchElementException("No feedback found for candidate $candidateId"))
        }
    }
}
