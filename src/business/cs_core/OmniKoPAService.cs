// Omni KoPA KG Completion Domain (C#)
// Ref: zjukg/KoPA — ACM MM 2024
using System;
using System.Collections.Generic;
using System.Linq;

namespace Omni.KoPA
{
    public record Triple(string Head, string Relation, string Tail);
    public record KGCompletionResult(string Query, List<(string Entity, double Score)> Candidates);

    public static class KoPAService
    {
        public static double TransEScore(double[] head, double[] rel, double[] tail)
        {
            double sum = 0;
            int d = Math.Min(head.Length, Math.Min(rel.Length, tail.Length));
            for (int i = 0; i < d; i++) { double diff = head[i] + rel[i] - tail[i]; sum += diff * diff; }
            return -sum;
        }

        public static KGCompletionResult RankCandidates(double[] head, double[] rel,
            List<(string Name, double[] Emb)> candidates, int topK = 10)
        {
            var scored = candidates.Select(c => (c.Name, TransEScore(head, rel, c.Emb)))
                                   .OrderByDescending(x => x.Item2).Take(topK).ToList();
            return new KGCompletionResult("completion", scored);
        }
    }
}
