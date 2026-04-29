using System;
using System.Text.RegularExpressions;

namespace Omni.Business.ASTCodeGenerator
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class SyntaxConstraints
    {
        public OmniResult<bool> VerifyIdentifierName(string identifier, string target_language)
        {
            if (string.IsNullOrEmpty(identifier) || string.IsNullOrEmpty(target_language))
            {
                return new OmniResult<bool>(new ArgumentException("Identifier and language must be provided"));
            }

            // Code Generation Business Logic: Naming Constraints
            // Ensures generated code variable names are valid for the target language (e.g., Rust, Go, C#)
            
            bool is_valid = false;
            
            if (target_language == "Rust" || target_language == "Python" || target_language == "Ruby")
            {
                // Snake case validation
                is_valid = Regex.IsMatch(identifier, @"^[a-z_][a-z0-9_]*$");
            }
            else if (target_language == "C#" || target_language == "Java" || target_language == "TypeScript")
            {
                // Camel case or Pascal case validation
                is_valid = Regex.IsMatch(identifier, @"^[a-zA-Z_][a-zA-Z0-9_]*$");
            }
            else
            {
                // Fallback generic constraint
                is_valid = Regex.IsMatch(identifier, @"^[a-zA-Z_][a-zA-Z0-9_]*$");
            }

            return new OmniResult<bool>(is_valid);
        }
    }
}
