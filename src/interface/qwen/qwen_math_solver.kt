data class OmniResult<T>(val isOk: Boolean, val value: T?, val error: String?)
class MathSolverActivity {
    private val maxProblemLen = 10000
    fun displaySolution(problem: String, solution: String, answer: String): OmniResult<Map<String, Any>> {
        if (problem.isEmpty()) return OmniResult(false, null, "Empty problem")
        if (problem.length > maxProblemLen) return OmniResult(false, null, "Problem exceeds $maxProblemLen")
        return OmniResult(true, mapOf("problem_len" to problem.length, "solution_len" to solution.length, "answer" to answer), null)
    }
}
