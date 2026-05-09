using System;
using System.Collections;
using UnityEngine;
using UnityEngine.Networking;

namespace Omni.Game.Dialogue
{
    public class OmniDialogueSystem : MonoBehaviour
    {
        [SerializeField] string apiEndpoint = "http://localhost:8080/api/v1/infer";
        [SerializeField] string npcName = "Guardian";
        bool isGenerating;
        public event Action<string> OnResponse;

        public void Send(string msg)
        {
            if (isGenerating) return;
            StartCoroutine(Infer(msg));
        }

        IEnumerator Infer(string prompt)
        {
            isGenerating = true;
            var json = JsonUtility.ToJson(new Req { prompt = prompt, max_tokens = 128 });
            using var req = new UnityWebRequest(apiEndpoint, "POST");
            req.uploadHandler = new UploadHandlerRaw(System.Text.Encoding.UTF8.GetBytes(json));
            req.downloadHandler = new DownloadHandlerBuffer();
            req.SetRequestHeader("Content-Type", "application/json");
            yield return req.SendWebRequest();
            var text = req.result == UnityWebRequest.Result.Success
                ? JsonUtility.FromJson<Res>(req.downloadHandler.text).generated_text
                : "The ancient wisdom escapes me...";
            OnResponse?.Invoke(text);
            isGenerating = false;
        }

        [Serializable] struct Req { public string prompt; public int max_tokens; }
        [Serializable] struct Res { public string generated_text; }
    }
}
