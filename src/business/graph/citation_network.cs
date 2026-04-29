using System;
using System.Collections.Generic;
using System.Linq;

namespace Omni.Business.Graph
{
    public class GraphResult<T>
    {
        public T Data { get; }
        public string Error { get; }
        public bool IsOk => Error == null;

        private GraphResult(T data, string error)
        {
            Data = data;
            Error = error;
        }

        public static GraphResult<T> Ok(T data) => new GraphResult<T>(data, null);
        public static GraphResult<T> Fail(string error) => new GraphResult<T>(default, error);
    }

    public class PaperNode
    {
        public string Id { get; set; }
        public string Title { get; set; }
        public int Year { get; set; }
        public HashSet<string> References { get; set; } = new HashSet<string>();
        public double PageRank { get; set; }
    }

    public class CitationNetworkManager
    {
        private readonly Dictionary<string, PaperNode> _papers = new Dictionary<string, PaperNode>();

        public GraphResult<bool> AddPaper(PaperNode paper)
        {
            if (paper == null || string.IsNullOrWhiteSpace(paper.Id))
            {
                return GraphResult<bool>.Fail("Invalid paper structure");
            }

            if (_papers.ContainsKey(paper.Id))
            {
                return GraphResult<bool>.Fail($"Paper {paper.Id} already exists in the network");
            }

            _papers[paper.Id] = paper;
            return GraphResult<bool>.Ok(true);
        }

        public GraphResult<bool> AddCitation(string sourceId, string targetId)
        {
            if (!_papers.ContainsKey(sourceId)) return GraphResult<bool>.Fail($"Source paper {sourceId} not found");
            if (!_papers.ContainsKey(targetId)) return GraphResult<bool>.Fail($"Target paper {targetId} not found");

            var source = _papers[sourceId];
            var target = _papers[targetId];

            // Domain rule: Cannot cite papers from the future
            if (target.Year > source.Year)
            {
                return GraphResult<bool>.Fail("Causality error: Cannot cite a paper published in the future");
            }

            source.References.Add(targetId);
            return GraphResult<bool>.Ok(true);
        }

        public GraphResult<List<string>> ComputeCoCitations(string paperA, string paperB)
        {
            try
            {
                // Papers that cite both paperA and paperB
                var coCitingPapers = _papers.Values
                    .Where(p => p.References.Contains(paperA) && p.References.Contains(paperB))
                    .Select(p => p.Id)
                    .ToList();

                return GraphResult<List<string>>.Ok(coCitingPapers);
            }
            catch (Exception ex)
            {
                return GraphResult<List<string>>.Fail($"Co-citation computation failed: {ex.Message}");
            }
        }

        public GraphResult<double> CalculateGraphDensity()
        {
            if (_papers.Count == 0) return GraphResult<double>.Ok(0.0);

            long possibleEdges = (long)_papers.Count * (_papers.Count - 1);
            if (possibleEdges == 0) return GraphResult<double>.Ok(0.0);

            long actualEdges = _papers.Values.Sum(p => p.References.Count);
            
            double density = (double)actualEdges / possibleEdges;
            return GraphResult<double>.Ok(density);
        }
    }
}
