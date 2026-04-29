using System;
using System.Collections.Generic;

namespace Omni.Business.VisionAimbot
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class Target
    {
        public int Id { get; set; }
        public double ScreenX { get; set; }
        public double ScreenY { get; set; }
        public double ThreatLevel { get; set; } // 0.0 to 1.0
    }

    public class TargetPrioritization
    {
        private readonly double _centerX;
        private readonly double _centerY;
        private readonly double _distanceWeight;
        private readonly double _threatWeight;

        public TargetPrioritization(double resolutionX, double resolutionY, double distanceWeight = 0.6, double threatWeight = 0.4)
        {
            _centerX = resolutionX / 2.0;
            _centerY = resolutionY / 2.0;
            _distanceWeight = distanceWeight;
            _threatWeight = threatWeight;
        }

        public OmniResult<Target> GetBestTarget(List<Target> detectedTargets)
        {
            if (detectedTargets == null || detectedTargets.Count == 0)
                return new OmniResult<Target>(new InvalidOperationException("No targets detected"));

            Target bestTarget = null;
            double highestScore = -1.0;

            foreach (var target in detectedTargets)
            {
                // Mathematical Euclidean distance from crosshair (center screen)
                double dx = target.ScreenX - _centerX;
                double dy = target.ScreenY - _centerY;
                double distance = Math.Sqrt(dx * dx + dy * dy);

                // Inverse distance (closer is better, max distance bounded deterministically)
                double maxDist = Math.Sqrt(_centerX * _centerX + _centerY * _centerY);
                double normDistScore = Math.Max(0.0, 1.0 - (distance / maxDist));

                // Weighted Business Rule evaluation
                double score = (normDistScore * _distanceWeight) + (target.ThreatLevel * _threatWeight);

                if (score > highestScore)
                {
                    highestScore = score;
                    bestTarget = target;
                }
            }

            return new OmniResult<Target>(bestTarget);
        }
    }
}
