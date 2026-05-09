using System;
using System.Collections.Generic;

namespace Omni.Domain.System
{
    public class EcosystemHealthSaga
    {
        public Guid CheckId { get; private set; }
        public DateTime InitiatedAt { get; private set; }
        public Dictionary<string, bool> LayerStatuses { get; private set; }
        
        public bool IsHealthy => EvaluateOverallHealth();

        public EcosystemHealthSaga()
        {
            CheckId = Guid.NewGuid();
            InitiatedAt = DateTime.UtcNow;
            LayerStatuses = new Dictionary<string, bool>
            {
                { "SystemLayer_Rust", false },
                { "NetworkLayer_Go", false },
                { "ComputeLayer_Python", false },
                { "ConcurrencyLayer_Elixir", false },
                { "InterfaceLayer_TypeScript", false }
            };
        }

        public void ReportLayerStatus(string layerName, bool isOperational)
        {
            if (LayerStatuses.ContainsKey(layerName))
            {
                LayerStatuses[layerName] = isOperational;
            }
        }

        private bool EvaluateOverallHealth()
        {
            foreach (var status in LayerStatuses.Values)
            {
                if (!status) return false;
            }
            return true; // Omnipresent health achieved
        }

        public string GetHealthReport()
        {
            return $"OMNI Ecosystem Health (ID: {CheckId}) - Status: {(IsHealthy ? "OPTIMAL" : "DEGRADED")}";
        }
    }
}
