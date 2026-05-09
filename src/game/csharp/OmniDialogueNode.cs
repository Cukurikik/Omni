// OMNI Framework - Dialogue Node (C#)
// Logic for branching dialogue trees generated dynamically by LLMs in Unity games

using System.Collections.Generic;
using UnityEngine;

namespace Omni.Game.AI
{
    [System.Serializable]
    public class DialogueOption
    {
        public string Text;
        public OmniDialogueNode NextNode;
    }

    [CreateAssetMenu(fileName = "NewDialogueNode", menuName = "OMNI/Dialogue Node")]
    public class OmniDialogueNode : ScriptableObject
    {
        [TextArea(3, 10)]
        public string NPCLine;
        
        public bool IsDynamicLLM = false;
        public string SystemPromptOverride;

        public List<DialogueOption> PlayerOptions = new List<DialogueOption>();

        // Dynamically generated options if IsDynamicLLM is true
        public List<DialogueOption> GenerateDynamicOptions(string playerHistory)
        {
            Debug.Log("OMNI C#: Requesting dynamic dialogue branch from LLM...");
            // In a real implementation, this would yield until the API returns
            // and parse the JSON into DialogueOption objects.
            
            return new List<DialogueOption>
            {
                new DialogueOption { Text = "[Generated] Agree with the NPC", NextNode = null },
                new DialogueOption { Text = "[Generated] Disagree violently", NextNode = null }
            };
        }
    }
}
