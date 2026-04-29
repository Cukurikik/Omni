using System;

namespace Omni.Business.Domain
{
    public class ModelRegistryAggregate
    {
        public Guid ModelId { get; private set; }
        public string Name { get; private set; }
        public string Version { get; private set; }
        public bool IsDeployed { get; private set; }

        public ModelRegistryAggregate(Guid id, string name, string version)
        {
            ModelId = id;
            Name = name;
            Version = version;
            IsDeployed = false;
        }

        public void Deploy()
        {
            if (IsDeployed) throw new Exception("Model is already deployed");
            IsDeployed = true;
        }
    }
}
