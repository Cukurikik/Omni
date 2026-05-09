using UnityEngine;

namespace OmniMoE.Game
{
    // OMNI MOTHER: Unity Gateway Load Visualizer

    public class OmniGatewayVisualizer : MonoBehaviour
    {
        public Light loadIndicator;

        public void UpdateLoad(float percentage)
        {
            if (loadIndicator != null)
            {
                loadIndicator.color = Color.Lerp(Color.green, Color.red, percentage);
            }
        }
    }
}
