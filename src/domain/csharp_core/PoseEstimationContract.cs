using System;

namespace Omni.Domain.Pose
{
    public class PoseEstimationContract
    {
        public Guid SessionId { get; }
        public int NumberOfViews { get; }

        public PoseEstimationContract(int views)
        {
            if (views <= 0) throw new ArgumentException("Number of views must be > 0");
            SessionId = Guid.NewGuid();
            NumberOfViews = views;
        }
    }
}
