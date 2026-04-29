// Omni M3Exam Business Service (C#)
// Ref: DAMO-NLP-SG/M3Exam
namespace Omni.Business.M3Exam {
    public static class ExamService {
        public static bool EvaluateMCQ(string prediction, string answer) {
            return prediction.Trim().ToUpper() == answer.Trim().ToUpper();
        }
        public static double BatchAccuracy(string[] predictions, string[] answers) {
            int correct = 0;
            for (int i = 0; i < System.Math.Min(predictions.Length, answers.Length); i++)
                if (EvaluateMCQ(predictions[i], answers[i])) correct++;
            return (double)correct / System.Math.Max(answers.Length, 1);
        }
    }
}
