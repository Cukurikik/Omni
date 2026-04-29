using System;

namespace Omni.Business.VisualQuestionAnswering
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class HallucinationFilters
    {
        public OmniResult<bool> ValidateGroundedResponse(string llm_text, int num_bounding_boxes)
        {
            if (string.IsNullOrEmpty(llm_text))
            {
                return new OmniResult<bool>(new ArgumentException("LLM text cannot be empty"));
            }

            // VQA Business Logic: Hallucination Prevention
            // If the Multimodal LLM claims to see an object but provides 0 bounding boxes for it,
            // it is likely hallucinating.
            
            bool claims_to_see_objects = llm_text.Contains("I see") || llm_text.Contains("There is") || llm_text.Contains("located at");
            
            if (claims_to_see_objects && num_bounding_boxes == 0)
            {
                // Hallucination detected: Claims objects exist but failed to ground them
                return new OmniResult<bool>(false);
            }
            
            return new OmniResult<bool>(true);
        }
    }
}
