using System;
using System.Collections.Generic;
using System.Linq;

namespace Omni.Business.Kaggle {
    public class SolutionEvaluator {
        public static double CalculateRMSE(List<double> actual, List<double> predicted) {
            if (actual.Count != predicted.Count || actual.Count == 0) return double.NaN;
            
            double sumSq = 0.0;
            for (int i = 0; i < actual.Count; i++) {
                double diff = actual[i] - predicted[i];
                sumSq += diff * diff;
            }
            return Math.Sqrt(sumSq / actual.Count);
        }
    }
}
