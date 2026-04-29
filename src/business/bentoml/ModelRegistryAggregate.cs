using System;
using System.Collections.Generic;

namespace Omni.Business.BentoML {
    public class ModelRegistryAggregate {
        public Guid RegistryId { get; private set; }
        private List<string> _registeredModels;

        public ModelRegistryAggregate(Guid id) {
            RegistryId = id;
            _registeredModels = new List<string>();
        }

        public void RegisterModel(string modelName) {
            if (string.IsNullOrWhiteSpace(modelName)) {
                throw new ArgumentException("Model name cannot be empty");
            }
            if (_registeredModels.Contains(modelName)) {
                throw new InvalidOperationException("Model already registered");
            }
            _registeredModels.Add(modelName);
        }

        public IReadOnlyList<string> GetModels() {
            return _registeredModels.AsReadOnly();
        }
    }
}
