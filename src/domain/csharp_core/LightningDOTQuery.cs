using System;

namespace Omni.Domain.Search
{
    public class LightningDOTQuery
    {
        public string Text { get; }

        public LightningDOTQuery(string text)
        {
            Text = text;
        }
    }
}
