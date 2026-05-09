// OMNI Framework - Unity C# Data Flow Visualizer
using UnityEngine;

public class OmniDataVisualizer : MonoBehaviour
{
    public GameObject dataPacketPrefab;
    public Transform sourceNode;
    public Transform destinationNode;
    
    private float spawnTimer = 0f;
    private float spawnRate = 0.5f;

    void Update()
    {
        spawnTimer += Time.deltaTime;
        if (spawnTimer >= spawnRate)
        {
            SpawnDataPacket();
            spawnTimer = 0f;
        }
    }

    void SpawnDataPacket()
    {
        if (dataPacketPrefab != null && sourceNode != null && destinationNode != null)
        {
            GameObject packet = Instantiate(dataPacketPrefab, sourceNode.position, Quaternion.identity);
            
            // Assuming the prefab has a script 'OmniPacketMove' that moves it towards a target
            packet.SendMessage("SetTarget", destinationNode, SendMessageOptions.DontRequireReceiver);
        }
    }
}
