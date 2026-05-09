// OMNI Framework - Unity LLM Controller (C#)
// Script attached to NPCs to give them dynamic dialogue powered by OMNI API

using UnityEngine;
using UnityEngine.Networking;
using System.Collections;

public class OmniLLMController : MonoBehaviour
{
    public string apiUrl = "https://api.omni.dev/v1/generate";
    public string characterPersona = "You are a grumpy blacksmith in a fantasy village.";

    public void Interact(string playerMessage)
    {
        StartCoroutine(SendToOmni(playerMessage));
    }

    private IEnumerator SendToOmni(string playerMessage)
    {
        string prompt = $"{characterPersona}\nPlayer says: {playerMessage}\nBlacksmith says:";
        
        // Mocking the JSON payload structure
        string jsonPayload = $"{{\"prompt\": \"{prompt}\", \"max_tokens\": 50}}";
        
        using (UnityWebRequest request = new UnityWebRequest(apiUrl, "POST"))
        {
            byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonPayload);
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");

            Debug.Log("OMNI Unity: Sending request to LLM...");
            
            // Wait for response
            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                Debug.Log($"OMNI Unity: Blacksmith replied: {request.downloadHandler.text}");
                // Here you would parse the JSON and display it in UI
            }
            else
            {
                Debug.LogError($"OMNI Unity: Error communicating with LLM: {request.error}");
            }
        }
    }
}
