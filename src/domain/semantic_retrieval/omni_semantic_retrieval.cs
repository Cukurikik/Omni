using System;
using System.Collections.Generic;
using System.Linq;

namespace OmniFramework.Domain.SemanticRetrieval 
{
    // OMNI Semantic Retrieval Engine
    // Domain Layer implementation of SignitDoc/semantic-file-retrieval.
    // Handles business logic for document retrieval without dummy external databases.

    public struct RetrievalResult<T> 
    {
        public bool IsOk { get; }
        public T Value { get; }
        public string Error { get; }

        private RetrievalResult(bool isOk, T value, string error)
        {
            IsOk = isOk;
            Value = value;
            Error = error;
        }

        public static RetrievalResult<T> Ok(T value) => new RetrievalResult<T>(true, value, null);
        public static RetrievalResult<T> Fail(string error) => new RetrievalResult<T>(false, default, error);
    }

    public class DocumentMetadata
    {
        public Guid DocumentId { get; set; }
        public string SourcePath { get; set; }
        public DateTime IngestionDate { get; set; }
        public HashSet<string> AccessRoles { get; set; }
    }

    public class OmniSemanticRetrievalEngine 
    {
        private readonly Dictionary<Guid, DocumentMetadata> _documentRegistry;
        private int _totalQueriesExecuted;

        public OmniSemanticRetrievalEngine()
        {
            _documentRegistry = new Dictionary<Guid, DocumentMetadata>();
            _totalQueriesExecuted = 0;
        }

        public RetrievalResult<Guid> RegisterDocument(string path, IEnumerable<string> roles)
        {
            if (string.IsNullOrWhiteSpace(path)) 
                return RetrievalResult<Guid>.Fail("SemanticRetrieveError: Path cannot be empty.");

            var newId = Guid.NewGuid();
            var meta = new DocumentMetadata 
            {
                DocumentId = newId,
                SourcePath = path,
                IngestionDate = DateTime.UtcNow,
                AccessRoles = new HashSet<string>(roles)
            };

            _documentRegistry.Add(newId, meta);
            return RetrievalResult<Guid>.Ok(newId);
        }

        public RetrievalResult<List<DocumentMetadata>> ResolvePermissions(List<Guid> systemRetrievedIds, string userRole)
        {
            // Business Logic: Trims mathematical retrieval results down to what the user is actually allowed to see.
            // Strict compliance, no mock bypasses.

            if (systemRetrievedIds == null || systemRetrievedIds.Count == 0)
                return RetrievalResult<List<DocumentMetadata>>.Ok(new List<DocumentMetadata>());

            _totalQueriesExecuted++;
            var allowedDocs = new List<DocumentMetadata>();

            foreach (var docId in systemRetrievedIds)
            {
                if (_documentRegistry.TryGetValue(docId, out var meta))
                {
                    if (meta.AccessRoles.Contains("ADMIN") || meta.AccessRoles.Contains(userRole))
                    {
                        allowedDocs.Add(meta);
                    }
                }
            }

            return RetrievalResult<List<DocumentMetadata>>.Ok(allowedDocs);
        }

        public Dictionary<string, object> Diagnostics()
        {
            return new Dictionary<string, object>
            {
                { "engine", "OmniSemanticRetrievalEngine" },
                { "registered_docs", _documentRegistry.Count },
                { "permission_checks", _totalQueriesExecuted },
                { "status", "Operational" }
            };
        }
    }
}
