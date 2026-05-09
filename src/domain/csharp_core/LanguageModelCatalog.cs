using System;
using System.Collections.Generic;

namespace Omni.Domain.Language
{
    public class LanguageModelCatalog
    {
        private readonly Dictionary<string, string> _models = new();

        public void RegisterModel(string id, string endpoint)
        {
            if (string.IsNullOrEmpty(id) || string.IsNullOrEmpty(endpoint))
                throw new ArgumentException("Invalid model registration details");
                
            _models[id] = endpoint;
        }

        public string GetEndpoint(string id)
        {
            return _models.TryGetValue(id, out var endpoint) ? endpoint : throw new Exception("Model not found");
        }
    }
}
