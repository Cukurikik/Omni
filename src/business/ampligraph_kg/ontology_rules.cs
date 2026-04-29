using System;
using System.Collections.Generic;

namespace Omni.Business.AmpligraphKG
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class OntologyRules
    {
        // Deterministic set of rules for ontology validation
        private readonly HashSet<string> _validRelations = new HashSet<string>
        {
            "is_a", "has_part", "located_in", "works_for"
        };

        public OmniResult<bool> ValidateTriple(string headType, string relation, string tailType)
        {
            if (string.IsNullOrWhiteSpace(headType) || string.IsNullOrWhiteSpace(tailType))
            {
                return new OmniResult<bool>(new ArgumentException("Entity types cannot be empty"));
            }

            if (!_validRelations.Contains(relation))
            {
                return new OmniResult<bool>(new ArgumentException($"Unknown relation: {relation}"));
            }

            // Domain specific business logic
            if (relation == "works_for" && headType != "Person")
            {
                return new OmniResult<bool>(false); // Only persons can work for someone/something
            }
            
            if (relation == "located_in" && tailType != "Location")
            {
                return new OmniResult<bool>(false); // Must be located in a Location
            }

            return new OmniResult<bool>(true);
        }
    }
}
