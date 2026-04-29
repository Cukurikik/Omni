// OMNI MOTHER - DIVINE MEMORY INTEGRATION
// Spring Inversion of Control Container (OMNI Zero-Mock Implementation)
// Implements mathematical dependency directed graph resolution.

using System;
using System.Collections.Generic;

namespace Omni.Compute.Spring
{
    public class Result<T>
    {
        public T Value { get; }
        public string Error { get; }
        public bool IsOk { get; }

        private Result(T val, string err, bool isOk)
        {
            Value = val;
            Error = err;
            IsOk = isOk;
        }

        public static Result<T> Ok(T val) => new Result<T>(val, null, true);
        public static Result<T> Err(string err) => new Result<T>(default(T), err, false);
    }

    public class IoCContainer
    {
        // Bean Name -> Dependencies (Names)
        private readonly Dictionary<string, List<string>> _beanDefinitions = new Dictionary<string, List<string>>();

        public void RegisterBeanDefinition(string beanName, List<string> dependencies)
        {
            _beanDefinitions[beanName] = dependencies ?? new List<string>();
        }

        // Detects circular dependencies traversing the dependency DAG exactly like Spring Context
        public Result<bool> ValidateContextGraph()
        {
            HashSet<string> visited = new HashSet<string>();
            HashSet<string> recursionStack = new HashSet<string>();

            foreach (var bean in _beanDefinitions.Keys)
            {
                if (DetectCycle(bean, visited, recursionStack))
                {
                    return Result<bool>.Err($"Circular dependency detected involving bean: {bean}");
                }
            }

            return Result<bool>.Ok(true);
        }

        private bool DetectCycle(string currentBean, HashSet<string> visited, HashSet<string> recursionStack)
        {
            if (recursionStack.Contains(currentBean)) return true; // Cycle
            if (visited.Contains(currentBean)) return false; // Already checked and clean

            visited.Add(currentBean);
            recursionStack.Add(currentBean);

            if (_beanDefinitions.ContainsKey(currentBean))
            {
                foreach (var dep in _beanDefinitions[currentBean])
                {
                    if (DetectCycle(dep, visited, recursionStack))
                    {
                        return true;
                    }
                }
            }

            recursionStack.Remove(currentBean);
            return false;
        }
    }
}
