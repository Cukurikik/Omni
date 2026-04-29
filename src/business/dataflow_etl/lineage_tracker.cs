using System;
using System.Collections.Generic;

namespace Omni.Business.DataflowETL
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class LineageNode
    {
        public string NodeId { get; set; }
        public string Transformation { get; set; }
        public long Timestamp { get; set; }
    }

    public class LineageTracker
    {
        private readonly Dictionary<string, LineageNode> _lineageGraph;

        public LineageTracker()
        {
            _lineageGraph = new Dictionary<string, LineageNode>();
        }

        public OmniResult<string> RegisterTransformation(string inputId, string outputId, string transform)
        {
            if (string.IsNullOrEmpty(outputId))
            {
                return new OmniResult<string>(new ArgumentException("Output ID cannot be null"));
            }

            var node = new LineageNode
            {
                NodeId = outputId,
                Transformation = $"{inputId} -> {transform}",
                Timestamp = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds()
            };

            _lineageGraph[outputId] = node;
            return new OmniResult<string>($"Registered: {outputId}");
        }

        public OmniResult<LineageNode> GetLineage(string outputId)
        {
            if (_lineageGraph.TryGetValue(outputId, out var node))
            {
                return new OmniResult<LineageNode>(node);
            }
            return new OmniResult<LineageNode>(new KeyNotFoundException($"Node {outputId} not found"));
        }
    }
}
