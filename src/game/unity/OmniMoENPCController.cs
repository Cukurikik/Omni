// OMNI Framework - MoE NPC Dialogue Controller (Unity C#)
// Integrates the local Unity game environment with the Omni MoE backend API
// for generating dynamic, context-aware NPC dialogues.

using UnityEngine;
using UnityEngine.Networking;
using System.Collections;
using System.Text;

namespace Omni.GameIntegration
{
    [System.Serializable]
    public class MoERequest
    {
        public string prompt;
        public int max_tokens;
    }

    [System.Serializable]
    public class MoEResponse
    {
        public string text;
    }

    public class OmniMoENPCController : MonoBehaviour
    {
        [Header("NPC Configuration")]
        public string npcName = "Eldrin";
        public string npcPersonality = "A wise, ancient wizard speaking in riddles.";

        [Header("API Settings")]
        public string omniServerUrl = "http://localhost:8082/v1/generate";

        public void SpeakToNPC(string playerInput)
        {
            Debug.Log($"[OMNI Unity] Player says to {npcName}: {playerInput}");
            StartCoroutine(FetchMoEResponse(playerInput));
        }

        private IEnumerator FetchMoEResponse(string playerInput)
        {
            string fullPrompt = $"System: You are {npcName}. {npcPersonality}\nPlayer: {playerInput}\n{npcName}:";
            
            MoERequest reqData = new MoERequest 
            { 
                prompt = fullPrompt, 
                max_tokens = 150 
            };

            string jsonData = JsonUtility.ToJson(reqData);
            
            using (UnityWebRequest request = new UnityWebRequest(omniServerUrl, "POST"))
            {
                byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonData);
                request.uploadHandler = new UploadHandlerRaw(bodyRaw);
                request.downloadHandler = new DownloadHandlerBuffer();
                request.SetRequestHeader("Content-Type", "application/json");

                yield return request.SendWebRequest();

                if (request.result == UnityWebRequest.Result.ConnectionError || request.result == UnityWebRequest.Result.ProtocolError)
                {
                    Debug.LogError($"[OMNI Unity] Error connecting to MoE backend: {request.error}");
                }
                else
                {
                    MoEResponse resData = JsonUtility.FromJson<MoEResponse>(request.downloadHandler.text);
                    Debug.Log($"[OMNI Unity] {npcName} replies: {resData.text}");
                    
                    // Trigger UI update or audio generation here
                }
            }
        }
    }
}
