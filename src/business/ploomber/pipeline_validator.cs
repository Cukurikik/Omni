using System;
using System.Collections.Generic;

// OMNI PLOOMBER: Pipeline Validator
// C# domain logic mapping dependencies and validating that pipelines contain no cycles (DAG constraint).
// Source: ploomber/ploomber

namespace Omni.Ploomber
{
    public class PipelineValidator
    {
        /// <summary>
        /// Validates that a given set of tasks and dependencies forms a valid Directed Acyclic Graph (DAG).
        /// Returns false if a cycle is detected.
        /// </summary>
        public bool IsValidDAG(Dictionary<string, List<string>> adjacencyList)
        {
            var visited = new HashSet<string>();
            var recursionStack = new HashSet<string>();

            foreach (var node in adjacencyList.Keys)
            {
                if (DetectCycleUtil(node, adjacencyList, visited, recursionStack))
                {
                    return false; // Cycle detected
                }
            }
            return true; // Valid DAG
        }

        private bool DetectCycleUtil(string v, Dictionary<string, List<string>> adj, HashSet<string> visited, HashSet<string> recStack)
        {
            if (recStack.Contains(v)) return true;
            if (visited.Contains(v)) return false;

            visited.Add(v);
            recStack.Add(v);

            if (adj.ContainsKey(v))
            {
                foreach (var neighbor in adj[v])
                {
                    if (DetectCycleUtil(neighbor, adj, visited, recStack))
                    {
                        return true;
                    }
                }
            }

            recStack.Remove(v);
            return false;
        }
    }
}
