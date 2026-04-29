using System;
using System.Collections.Generic;

namespace Omni.Business.PassGAN
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class StrengthEvaluator
    {
        private readonly double _minEntropyBits;

        public StrengthEvaluator(double minEntropyBits = 50.0)
        {
            _minEntropyBits = minEntropyBits;
        }

        public OmniResult<PasswordAssessment> EvaluateStrength(string password)
        {
            if (string.IsNullOrEmpty(password))
                return new OmniResult<PasswordAssessment>(new ArgumentException("Password cannot be null or empty"));

            // Mathematical Entropy calculation: E = L * log2(R)
            // L = length, R = character pool size

            int poolSize = 0;
            bool hasLower = false, hasUpper = false, hasDigit = false, hasSpecial = false;

            foreach (char c in password)
            {
                if (char.IsLower(c)) hasLower = true;
                else if (char.IsUpper(c)) hasUpper = true;
                else if (char.IsDigit(c)) hasDigit = true;
                else hasSpecial = true;
            }

            if (hasLower) poolSize += 26;
            if (hasUpper) poolSize += 26;
            if (hasDigit) poolSize += 10;
            if (hasSpecial) poolSize += 32;

            if (poolSize == 0) poolSize = 1; // Fallback

            double entropy = password.Length * Math.Log2(poolSize);
            bool isStrong = entropy >= _minEntropyBits;

            var assessment = new PasswordAssessment
            {
                PasswordLength = password.Length,
                PoolSize = poolSize,
                EntropyBits = entropy,
                MeetsPolicy = isStrong
            };

            return new OmniResult<PasswordAssessment>(assessment);
        }
    }

    public class PasswordAssessment
    {
        public int PasswordLength { get; set; }
        public int PoolSize { get; set; }
        public double EntropyBits { get; set; }
        public bool MeetsPolicy { get; set; }
    }
}
