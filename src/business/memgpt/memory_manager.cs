using System;
using System.Collections.Generic;
using System.Linq;

namespace Omni.Business.MemGPT
{
    /// <summary>
    /// OMNI MemGPT: Memory Tiering Manager
    /// OS-like virtual memory management for LLM contexts (Working Memory vs Archival Memory).
    /// Source: memgpt/MemGPT
    /// </summary>

    public class MemoryTierError : Exception
    {
        public MemoryTierError(string message) : base(message) {}
    }

    public class WorkingMemory
    {
        public int CoreTokenLimit { get; }
        public List<string> PersonaBlock { get; }
        public List<string> HumanBlock { get; }
        public List<string> MessageQueue { get; } // FIFO

        public WorkingMemory(int coreTokenLimit = 2000)
        {
            CoreTokenLimit = coreTokenLimit;
            PersonaBlock = new List<string>();
            HumanBlock = new List<string>();
            MessageQueue = new List<string>();
        }

        public int CurrentTokenEstimate()
        {
            // Naive estimation: length / 4
            int chars = PersonaBlock.Sum(s => s.Length) + 
                        HumanBlock.Sum(s => s.Length) + 
                        MessageQueue.Sum(s => s.Length);
            return chars / 4;
        }
    }

    public class MemoryManager
    {
        private readonly WorkingMemory _workingMemory;
        // In a real system, archival storage connects to an SQL/Vector DB.
        private readonly List<string> _archivalStorageMock; 

        public MemoryManager(int workingLimit)
        {
            _workingMemory = new WorkingMemory(workingLimit);
            _archivalStorageMock = new List<string>();
        }

        /// <summary>
        /// Attempts to append a message to the working context.
        /// If the token limit is exceeded, it initiates an eviction strategy (paging out).
        /// </summary>
        public void AppendMessage(string message)
        {
            if (string.IsNullOrEmpty(message)) return;

            int messageTokens = message.Length / 4;

            if (_workingMemory.CurrentTokenEstimate() + messageTokens > _workingMemory.CoreTokenLimit)
            {
                EvictOldestMessages(messageTokens);
            }

            _workingMemory.MessageQueue.Add(message);
        }

        private void EvictOldestMessages(int requiredTokens)
        {
            while (_workingMemory.MessageQueue.Count > 0 && 
                   _workingMemory.CurrentTokenEstimate() + requiredTokens > _workingMemory.CoreTokenLimit)
            {
                // Evict FIFO (Page Out to Archival)
                string oldest = _workingMemory.MessageQueue[0];
                _workingMemory.MessageQueue.RemoveAt(0);
                
                // Write to Archival DB
                _archivalStorageMock.Add(oldest);
            }

            if (_workingMemory.CurrentTokenEstimate() + requiredTokens > _workingMemory.CoreTokenLimit)
            {
                throw new MemoryTierError("Cannot free enough tokens. Core blocks (Persona/Human) are too large.");
            }
        }

        public string CompileContextPrompt()
        {
            var prompt = "SYSTEM INSTRUCTIONS:\n";
            prompt += string.Join("\n", _workingMemory.PersonaBlock) + "\n";
            prompt += "USER CONTEXT:\n";
            prompt += string.Join("\n", _workingMemory.HumanBlock) + "\n";
            prompt += "RECENT MESSAGES:\n";
            prompt += string.Join("\n", _workingMemory.MessageQueue) + "\n";
            return prompt;
        }
    }
}
