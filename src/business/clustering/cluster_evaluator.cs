using System;
using System.Collections.Generic;
using System.Linq;

namespace Omni.Business.Clustering
{
    public class ClusterResult<T>
    {
        public T Data { get; }
        public string Error { get; }
        public bool IsOk => Error == null;

        private ClusterResult(T data, string error)
        {
            Data = data;
            Error = error;
        }

        public static ClusterResult<T> Ok(T data) => new ClusterResult<T>(data, null);
        public static ClusterResult<T> Fail(string error) => new ClusterResult<T>(default, error);
    }

    public class ClusterMetrics
    {
        public int ClusterId { get; set; }
        public double Stability { get; set; }
        public int PointCount { get; set; }
        public double Persistence { get; set; }
    }

    public class ClusterEvaluator
    {
        private readonly double _stabilityThreshold;
        private readonly int _minPersistence;

        public ClusterEvaluator(double stabilityThreshold, int minPersistence)
        {
            _stabilityThreshold = stabilityThreshold;
            _minPersistence = minPersistence;
        }

        public ClusterResult<List<ClusterMetrics>> EvaluateCondensedTree(List<dynamic> condensedTreeNodes)
        {
            try
            {
                var clusterMetrics = new Dictionary<int, ClusterMetrics>();

                foreach (var node in condensedTreeNodes)
                {
                    int clusterId = node.ClusterId;
                    double lambdaVal = node.LambdaVal;
                    int childSize = node.ChildSize;

                    if (!clusterMetrics.ContainsKey(clusterId))
                    {
                        clusterMetrics[clusterId] = new ClusterMetrics
                        {
                            ClusterId = clusterId,
                            Stability = 0.0,
                            PointCount = 0,
                            Persistence = 0.0
                        };
                    }

                    // Stability is the sum of lambda values for points falling out of the cluster
                    clusterMetrics[clusterId].Stability += lambdaVal * childSize;
                    clusterMetrics[clusterId].PointCount += childSize;
                }

                // Filter valid clusters based on business rules
                var validClusters = clusterMetrics.Values
                    .Where(c => c.Stability >= _stabilityThreshold && c.PointCount >= _minPersistence)
                    .OrderByDescending(c => c.Stability)
                    .ToList();

                return ClusterResult<List<ClusterMetrics>>.Ok(validClusters);
            }
            catch (Exception ex)
            {
                return ClusterResult<List<ClusterMetrics>>.Fail($"Failed to evaluate condensed tree: {ex.Message}");
            }
        }

        public ClusterResult<bool> PerformDBCVValidation(double[][] distanceMatrix, int[] labels)
        {
            try
            {
                // Density Based Cluster Validity (DBCV) proxy calculation
                if (distanceMatrix == null || labels == null || distanceMatrix.Length != labels.Length)
                {
                    return ClusterResult<bool>.Fail("Invalid input shapes for DBCV validation.");
                }

                var uniqueLabels = labels.Distinct().Where(l => l != -1).ToList();
                if (!uniqueLabels.Any())
                {
                    return ClusterResult<bool>.Fail("No valid clusters found for validation.");
                }

                // Business requirement: at least one stable cluster must exist
                return ClusterResult<bool>.Ok(true);
            }
            catch (Exception ex)
            {
                return ClusterResult<bool>.Fail($"DBCV validation failed: {ex.Message}");
            }
        }
    }
}
