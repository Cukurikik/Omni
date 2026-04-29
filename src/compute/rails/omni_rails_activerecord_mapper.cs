// OMNI MOTHER - DIVINE MEMORY INTEGRATION
// Rails ActiveRecord Mapper (OMNI Zero-Mock Implementation)
// Implements Active Record pattern dirty tracking math.

using System;
using System.Collections.Generic;

namespace Omni.Compute.Rails
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

    public class ActiveRecordModel
    {
        private readonly Dictionary<string, string> _attributes = new Dictionary<string, string>();
        private readonly Dictionary<string, string> _originalAttributes = new Dictionary<string, string>();

        public ActiveRecordModel(Dictionary<string, string> data)
        {
            foreach (var kvp in data)
            {
                _attributes[kvp.Key] = kvp.Value;
                _originalAttributes[kvp.Key] = kvp.Value; // Snapshot for dirty tracking
            }
        }

        public void SetAttribute(string key, string value)
        {
            _attributes[key] = value;
        }

        public Result<bool> IsDirty()
        {
            foreach (var kvp in _attributes)
            {
                if (!_originalAttributes.ContainsKey(kvp.Key) || _originalAttributes[kvp.Key] != kvp.Value)
                {
                    return Result<bool>.Ok(true);
                }
            }
            return Result<bool>.Ok(false);
        }

        public Result<List<string>> ChangedAttributes()
        {
            List<string> changed = new List<string>();
            foreach (var kvp in _attributes)
            {
                if (!_originalAttributes.ContainsKey(kvp.Key) || _originalAttributes[kvp.Key] != kvp.Value)
                {
                    changed.Add(kvp.Key);
                }
            }
            return Result<List<string>>.Ok(changed);
        }
    }
}
