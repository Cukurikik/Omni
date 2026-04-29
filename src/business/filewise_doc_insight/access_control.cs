using System;

namespace Omni.Business.FilewiseDocInsight
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class AccessControl
    {
        public OmniResult<bool> VerifyDocumentAccess(string user_role, string doc_classification)
        {
            if (string.IsNullOrEmpty(user_role) || string.IsNullOrEmpty(doc_classification))
            {
                return new OmniResult<bool>(new ArgumentException("Role and classification must be provided"));
            }

            // FileWise Business Logic: Enterprise Document Access Rules
            // Ensures RAG pipelines do not leak sensitive documents to unauthorized users
            
            if (user_role == "ADMIN") return new OmniResult<bool>(true);
            
            if (doc_classification == "TOP_SECRET") return new OmniResult<bool>(false);
            
            if (doc_classification == "INTERNAL" && user_role == "GUEST") return new OmniResult<bool>(false);

            return new OmniResult<bool>(true);
        }
    }
}
