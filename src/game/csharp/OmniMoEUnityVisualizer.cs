using UnityEngine;

namespace OmniMoE.Game
{
    // OMNI MOTHER: Game & Simulation Layer
    // 3D Visualizer for MoE Routing paths using Unity3D

    public class OmniMoEUnityVisualizer : MonoBehaviour
    {
        public GameObject tokenPrefab;
        public Transform[] expertNodes;

        void Start()
        {
            Debug.Log("[OMNI MOTHER] Initializing 3D MoE Visualizer.");
        }

        public void RouteToken(int expertId)
        {
            if (expertId >= 0 && expertId < expertNodes.Length)
            {
                GameObject token = Instantiate(tokenPrefab, Vector3.zero, Quaternion.identity);
                // In production, use a Coroutine or DOTween to animate to the expertNode
                token.transform.position = expertNodes[expertId].position;
            }
        }
    }
}
