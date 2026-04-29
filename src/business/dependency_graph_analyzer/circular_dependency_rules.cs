using System;

namespace Omni.Business.DependencyGraphAnalyzer
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class CircularDependencyRules
    {
        public OmniResult<bool> AllowCircularDependency(string package_a, string package_b, bool is_test_dependency)
        {
            if (string.IsNullOrEmpty(package_a) || string.IsNullOrEmpty(package_b))
            {
                return new OmniResult<bool>(new ArgumentException("Package names cannot be empty"));
            }

            // Dependency Business Logic: Circular Resolution
            // OMNI strictly forbids circular dependencies in production code to guarantee clean architecture
            
            if (is_test_dependency)
            {
                // Test dependencies (dev-dependencies) are allowed to be circular 
                // to support complex mocking/stubbing if needed
                return new OmniResult<bool>(true);
            }
            
            // Production dependencies CANNOT be circular
            return new OmniResult<bool>(false);
        }
    }
}
