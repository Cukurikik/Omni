using UnityEngine;

namespace OmniMoE.Game
{
    // OMNI MOTHER: 3D Node Status Visualizer

    public class OmniMoENodeVisualizer : MonoBehaviour
    {
        public Renderer nodeMaterial;

        public void SetHealth(bool isHealthy)
        {
            if (nodeMaterial != null)
            {
                nodeMaterial.material.color = isHealthy ? Color.green : Color.red;
            }
        }
    }
}
