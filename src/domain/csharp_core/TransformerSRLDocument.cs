using System;

namespace Omni.Domain.Linguistics
{
    public class TransformerSRLDocument
    {
        public string Content { get; }

        public TransformerSRLDocument(string content)
        {
            Content = content;
        }
    }
}
