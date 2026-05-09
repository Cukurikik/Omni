// OMNI Game — Unity C# Agent Controller
using UnityEngine;
using System.Collections;

namespace OmniFramework.Game
{
    public class OmniAgentController : MonoBehaviour
    {
        public string omniEndpoint = "http://localhost:8080/v1/action";
        private Vector3 targetPosition;

        void Start()
        {
            targetPosition = transform.position;
            StartCoroutine(RequestNextActionRoutine());
        }

        void Update()
        {
            // Smoothly move towards the AI-decided target
            transform.position = Vector3.Lerp(transform.position, targetPosition, Time.deltaTime * 2f);
        }

        IEnumerator RequestNextActionRoutine()
        {
            while (true)
            {
                // Simulate HTTP request to LLM to get next action based on environment state
                yield return new WaitForSeconds(3f);
                
                // Mock response processing
                float randomX = Random.Range(-5f, 5f);
                float randomZ = Random.Range(-5f, 5f);
                targetPosition = new Vector3(randomX, transform.position.y, randomZ);
                
                Debug.Log($"OMNI Agent commanded to move to: {targetPosition}");
            }
        }
    }
}
