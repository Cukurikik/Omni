using UnityEngine;
using System.Collections.Generic;

namespace Omni.UI.MoE
{
    // OMNI MOTHER Production Zero-Mock Unity Visualizer
    // C# Script for Unity3D to visualize MoE Neural Network Routing dynamically.

    public class NetworkVisualizer : MonoBehaviour
    {
        public GameObject nodePrefab;
        public GameObject linkPrefab;

        private List<GameObject> activeNodes = new List<GameObject>();

        void Start()
        {
            GenerateNetworkTopology(8); // 8 Experts
        }

        void GenerateNetworkTopology(int expertCount)
        {
            // Create Router Node (Center)
            GameObject router = Instantiate(nodePrefab, Vector3.zero, Quaternion.identity);
            router.name = "Router";
            router.GetComponent<Renderer>().material.color = Color.cyan;

            float radius = 5.0f;

            // Create Experts in a circle
            for (int i = 0; i < expertCount; i++)
            {
                float angle = i * Mathf.PI * 2 / expertCount;
                Vector3 pos = new Vector3(Mathf.Cos(angle) * radius, Mathf.Sin(angle) * radius, 0);
                
                GameObject expert = Instantiate(nodePrefab, pos, Quaternion.identity);
                expert.name = "Expert_" + i;
                expert.GetComponent<Renderer>().material.color = Color.gray;
                activeNodes.Add(expert);

                // Draw line
                DrawLink(router.transform.position, expert.transform.position);
            }
        }

        void DrawLink(Vector3 start, Vector3 end)
        {
            GameObject link = Instantiate(linkPrefab);
            LineRenderer lr = link.GetComponent<LineRenderer>();
            
            if (lr != null)
            {
                lr.SetPosition(0, start);
                lr.SetPosition(1, end);
                lr.startWidth = 0.1f;
                lr.endWidth = 0.1f;
                lr.material.color = new Color(0, 1, 1, 0.2f);
            }
        }

        // Called externally to animate routing
        public void HighlightRoute(int[] expertIndices)
        {
            foreach (var node in activeNodes)
            {
                node.GetComponent<Renderer>().material.color = Color.gray;
            }

            foreach (int index in expertIndices)
            {
                if (index >= 0 && index < activeNodes.Count)
                {
                    activeNodes[index].GetComponent<Renderer>().material.color = Color.green;
                }
            }
        }
    }
}
