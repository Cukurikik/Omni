using System;

namespace Omni.Domain.Chat
{
    public class YurenBaichuanSession
    {
        public Guid SessionId { get; }

        public YurenBaichuanSession()
        {
            SessionId = Guid.NewGuid();
        }
    }
}
