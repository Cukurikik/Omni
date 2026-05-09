// OMNI Domain Layer: C# Event Sourcing Store
using System.Collections.Generic;

namespace OmniFramework.Domain {
    public class OmniEventStore {
        private readonly List<string> _events = new List<string>();
        public void Append(string ev) => _events.Add(ev);
    }
}
