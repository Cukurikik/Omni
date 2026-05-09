// OMNI Game — Unity C# Environment Sensor
using UnityEngine;

namespace OmniFramework.Game
{
    public class OmniEnvironmentSensor : MonoBehaviour
    {
        public float scanRadius = 10f;
        public LayerMask interactableLayer;

        // Called by OmniAgentController to get local context
        public string GetSurroundingsContext()
        {
            Collider[] hits = Physics.OverlapSphere(transform.position, scanRadius, interactableLayer);
            
            if (hits.Length == 0) return "Area is clear.";

            string context = "I see: ";
            foreach (var hit in hits)
            {
                context += $"{hit.gameObject.name} at distance {Vector3.Distance(transform.position, hit.transform.position):F1}m. ";
            }
            return context;
        }

        private void OnDrawGizmosSelected()
        {
            Gizmos.color = Color.yellow;
            Gizmos.DrawWireSphere(transform.position, scanRadius);
        }
    }
}
