using System;
using System.Collections.Generic;

namespace Omni.Business.DVCVersioning
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class DAGValidator
    {
        public OmniResult<bool> ValidateDependencyDAG(List<Tuple<string, string>> dependencies)
        {
            if (dependencies == null) return new OmniResult<bool>(new ArgumentException("Dependencies cannot be null"));

            // Build adjacency list
            var adj = new Dictionary<string, List<string>>();
            foreach (var dep in dependencies)
            {
                if (!adj.ContainsKey(dep.Item1)) adj[dep.Item1] = new List<string>();
                adj[dep.Item1].Add(dep.Item2);
            }

            var visited = new HashSet<string>();
            var recStack = new HashSet<string>();

            bool DetectCycle(string node)
            {
                visited.Add(node);
                recStack.Add(node);

                if (adj.ContainsKey(node))
                {
                    foreach (var neighbor in adj[node])
                    {
                        if (!visited.Contains(neighbor))
                        {
                            if (DetectCycle(neighbor)) return true;
                        }
                        else if (recStack.Contains(neighbor))
                        {
                            return true;
                        }
                    }
                }

                recStack.Remove(node);
                return false;
            }

            foreach (var node in adj.Keys)
            {
                if (!visited.Contains(node))
                {
                    if (DetectCycle(node))
                    {
                        return new OmniResult<bool>(new InvalidOperationException("Cycle detected in DVC stage dependencies. Pipelines must be DAGs."));
                    }
                }
            }

            return new OmniResult<bool>(true);
        }
    }
}
