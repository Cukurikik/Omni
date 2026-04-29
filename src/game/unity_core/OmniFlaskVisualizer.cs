// Omni FLASK Eval Visualizer (Unity C#)
// Ref: kaistAI/FLASK — ICLR 2024
using UnityEngine;
using System.Collections.Generic;

namespace Omni.FLASK.Unity
{
    [System.Serializable]
    public struct SkillBar { public string SkillName; public float Score; }

    public class FlaskVisualizer : MonoBehaviour
    {
        public List<SkillBar> Skills = new List<SkillBar>();

        public float ComputeOverall()
        {
            if (Skills.Count == 0) return 0f;
            float sum = 0f;
            foreach (var s in Skills) sum += s.Score;
            return sum / Skills.Count;
        }

        public Color GetScoreColor(float score)
        {
            if (score >= 4f) return Color.green;
            if (score >= 3f) return Color.yellow;
            if (score >= 2f) return new Color(1f, 0.5f, 0f);
            return Color.red;
        }
    }
}
