// Omni GPA-LM Game Agent Evaluator (C#)
// Business Layer: Evaluation framework for game-playing agents with multimodal models.
// Ref: BAAI-Agents/GPA-LM — Game Playing Agents Survey.

namespace Omni.Business.GpaLm
{
    public readonly struct GameEvalResult
    {
        public double WinRate { get; init; }
        public double AvgReward { get; init; }
        public int TotalEpisodes { get; init; }
    }

    public static class OmniGpaEvaluator
    {
        public static GameEvalResult Evaluate(int wins, int total, double sumReward)
        {
            if (total <= 0) return new GameEvalResult { WinRate = 0, AvgReward = 0, TotalEpisodes = 0 };
            return new GameEvalResult
            {
                WinRate = Math.Round((double)wins / total, 6),
                AvgReward = Math.Round(sumReward / total, 6),
                TotalEpisodes = total
            };
        }
    }
}
