using System;

namespace Omni.Business.PyKeenKGE
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class EntityBounds
    {
        private readonly int _maxEntities;
        private readonly int _maxRelations;

        public EntityBounds(int maxEntities = 1000000, int maxRelations = 50000)
        {
            _maxEntities = maxEntities;
            _maxRelations = maxRelations;
        }

        public OmniResult<bool> ValidateTriple(int headId, int relationId, int tailId)
        {
            if (headId < 0 || headId >= _maxEntities)
                return new OmniResult<bool>(new ArgumentOutOfRangeException($"Head ID {headId} out of bounds"));

            if (tailId < 0 || tailId >= _maxEntities)
                return new OmniResult<bool>(new ArgumentOutOfRangeException($"Tail ID {tailId} out of bounds"));

            if (relationId < 0 || relationId >= _maxRelations)
                return new OmniResult<bool>(new ArgumentOutOfRangeException($"Relation ID {relationId} out of bounds"));

            // Business rule: Head cannot equal Tail for specific acyclic relation types
            // Deterministic constraint for hierarchy relations (assuming even relation IDs are hierarchical)
            if (relationId % 2 == 0 && headId == tailId)
            {
                return new OmniResult<bool>(new InvalidOperationException("Self-referential triples not allowed on hierarchical relations"));
            }

            return new OmniResult<bool>(true);
        }
    }
}
