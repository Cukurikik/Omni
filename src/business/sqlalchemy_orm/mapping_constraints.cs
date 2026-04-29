using System;
using System.Collections.Generic;

namespace Omni.Business.SqlAlchemyORM
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class MappingConstraints
    {
        public OmniResult<bool> ValidateRelationship(string parent_table, string child_table, bool is_one_to_many, bool is_nullable)
        {
            if (string.IsNullOrEmpty(parent_table) || string.IsNullOrEmpty(child_table))
            {
                return new OmniResult<bool>(new ArgumentException("Table names cannot be empty"));
            }

            if (parent_table == child_table)
            {
                 // Business Rule: Self-referential relationships require explicit foreign key naming, 
                 // which we simplify here by rejecting direct name equality without aliases.
                 return new OmniResult<bool>(new InvalidOperationException("Self-referential relationships require explicit alias mappings"));
            }

            // Strong domain constraint: One-to-Many children must have a NOT NULL foreign key 
            // if we are enforcing strict cascading deletes in our ORM architecture.
            if (is_one_to_many && is_nullable)
            {
                 return new OmniResult<bool>(new InvalidOperationException("One-to-Many relationships require non-nullable foreign keys for strict cascade compliance"));
            }

            return new OmniResult<bool>(true);
        }
    }
}
