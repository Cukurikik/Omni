// OMNI Domain Layer - CoE Evaluation Rules
using System;

namespace Omni.Domain.ChainOfEmbedding {
    public enum EvalError { None, InvalidConvergence }

    public class Result<T> {
        public T Value { get; }
        public EvalError Error { get; }
        public bool IsOk => Error == EvalError.None;

        public Result(T value) { Value = value; Error = EvalError.None; }
        public Result(EvalError error) { Error = error; }
    }

    public class Evaluator {
        public Result<bool> IsSelfEvaluationValid(double convergenceScore) {
            if (convergenceScore < 0) {
                return new Result<bool>(EvalError.InvalidConvergence);
            }
            
            // Lower convergence ratio means the chain settled in latent space
            bool isValid = convergenceScore < 0.5;
            return new Result<bool>(isValid);
        }
    }
}
