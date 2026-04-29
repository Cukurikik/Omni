// Omni DuQuant Calibration Service (C#)
using System; using System.Linq;
namespace Omni.DuQuant {
    public static class DuQuantService {
        public static double OutlierRatio(double[] weights, double thresholdStd = 3.0) {
            double mean = weights.Average(); double std = Math.Sqrt(weights.Average(w => (w-mean)*(w-mean)));
            return Math.Round((double)weights.Count(w => Math.Abs(w-mean) > thresholdStd*std) / weights.Length, 6);
        }
        public static double MemorySavingsGB(double paramsB, int origBits, int targetBits) {
            return Math.Round(paramsB * 1e9 * (origBits - targetBits) / 8 / 1e9, 2);
        }
    }
}
