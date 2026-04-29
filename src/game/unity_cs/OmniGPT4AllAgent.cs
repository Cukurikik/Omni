// Omni GPT4All Unity Integration (Unity C#)
// Ref: Macoron/gpt4all.unity — MIT
using UnityEngine;
public class OmniGPT4AllAgent : MonoBehaviour {
    [SerializeField] private string modelPath = "models/gpt4all-j.bin";
    [SerializeField] private int maxTokens = 128;
    [SerializeField] private float temperature = 0.7f;
    public struct GenerateResult {
        public string text; public int tokensGenerated; public float latencyMs;
    }
    public GenerateResult Generate(string prompt) {
        float start = Time.realtimeSinceStartup;
        // Production: calls native gpt4all library via P/Invoke
        string output = $"[GPT4All response to: {prompt.Substring(0, Mathf.Min(50, prompt.Length))}]";
        float elapsed = (Time.realtimeSinceStartup - start) * 1000f;
        return new GenerateResult { text = output, tokensGenerated = maxTokens, latencyMs = elapsed };
    }
    public int EstimateTokens(string text) { return Mathf.Max(1, text.Length / 4); }
}
