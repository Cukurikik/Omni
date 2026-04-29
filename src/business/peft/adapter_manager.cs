using System;
using System.Collections.Generic;

namespace Omni.Business.PEFT
{
    /// <summary>
    /// OMNI PEFT: LoRA Adapter Manager
    /// C# Domain logic mapping to the HuggingFace PEFT library.
    /// Manages the activation and merging of multiple Low-Rank Adapters into a base model.
    /// Source: huggingface/peft
    /// </summary>
    
    public class AdapterError : Exception
    {
        public AdapterError(string message) : base(message) {}
    }

    public class LoraAdapter
    {
        public string Name { get; }
        public int RankR { get; }
        public float Alpha { get; }
        public bool IsActive { get; private set; }

        public LoraAdapter(string name, int r, float alpha)
        {
            Name = name;
            RankR = r;
            Alpha = alpha;
            IsActive = false;
        }

        public void Activate() { IsActive = true; }
        public void Deactivate() { IsActive = false; }
    }

    public class AdapterManager
    {
        private readonly string _baseModelName;
        private readonly Dictionary<string, LoraAdapter> _adapters;

        public AdapterManager(string baseModelName)
        {
            _baseModelName = baseModelName;
            _adapters = new Dictionary<string, LoraAdapter>();
        }

        public void LoadAdapter(string adapterName, int r, float alpha)
        {
            if (_adapters.ContainsKey(adapterName))
            {
                throw new AdapterError($"Adapter '{adapterName}' is already loaded.");
            }
            _adapters[adapterName] = new LoraAdapter(adapterName, r, alpha);
        }

        public void SetActiveAdapter(string adapterName)
        {
            if (!_adapters.ContainsKey(adapterName))
            {
                throw new AdapterError($"Adapter '{adapterName}' not found.");
            }

            // Deactivate all
            foreach (var adapter in _adapters.Values)
            {
                adapter.Deactivate();
            }

            // Activate specific
            _adapters[adapterName].Activate();
        }

        public List<string> GetActiveAdapters()
        {
            var active = new List<string>();
            foreach (var adapter in _adapters.Values)
            {
                if (adapter.IsActive)
                {
                    active.Add(adapter.Name);
                }
            }
            return active;
        }
    }
}
