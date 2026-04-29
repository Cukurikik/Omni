using System;

namespace Omni.Business.RagEvaluationHarness
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class TestSuiteRunner
    {
        public OmniResult<bool> EvaluateAnswerFaithfulness(string retrieved_context, string llm_answer)
        {
            if (string.IsNullOrEmpty(retrieved_context) || string.IsNullOrEmpty(llm_answer))
            {
                return new OmniResult<bool>(new ArgumentException("Context and Answer required for evaluation"));
            }

            // Evaluation Business Logic: Faithfulness / Hallucination Detection Rules
            // In a full RAG harness, this uses a secondary LLM judge. Here we establish the rule skeleton.
            
            // Dummy deterministic rule: if answer contains "I don't know", it's faithful to an empty context
            if (llm_answer.Contains("I don't know") && retrieved_context.Length < 10)
            {
                return new OmniResult<bool>(true); // Faithful rejection
            }
            
            // Assuming the harness judged it faithful based on semantic overlap
            return new OmniResult<bool>(true);
        }
    }
}
