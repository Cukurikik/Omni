// Omni IEPile IE Domain Service (C#)
// Ref: zjunlp/IEPile — ACL 2024
using System;
using System.Collections.Generic;
using System.Linq;

namespace Omni.IEPile
{
    public record ExtractedEntity(string Text, string Type, int Start, int End);
    public record IEResult(string Task, List<ExtractedEntity> Entities, double Confidence);

    public static class IEPileService
    {
        public static IEResult BuildNERResult(string text, List<ExtractedEntity> entities)
        {
            double confidence = entities.Count > 0 ? Math.Min(1.0, entities.Count * 0.15) : 0;
            return new IEResult("NER", entities, Math.Round(confidence, 4));
        }

        public static (double Precision, double Recall, double F1) ComputeF1(
            List<ExtractedEntity> predicted, List<ExtractedEntity> gold)
        {
            var predSet = new HashSet<string>(predicted.Select(e => $"{e.Text}:{e.Type}"));
            var goldSet = new HashSet<string>(gold.Select(e => $"{e.Text}:{e.Type}"));
            int tp = predSet.Intersect(goldSet).Count();
            double p = tp / Math.Max(predSet.Count, 1.0);
            double r = tp / Math.Max(goldSet.Count, 1.0);
            double f1 = (p + r) > 0 ? 2 * p * r / (p + r) : 0;
            return (Math.Round(p, 4), Math.Round(r, 4), Math.Round(f1, 4));
        }
    }
}
