using System;

namespace Omni.Business.RL
{
    public class OUNoise
    {
        private double _state;
        public Result<double, string> Sample()
        {
            _state += -0.15 * _state + 0.2 * (new Random().NextDouble() - 0.5);
            return Result<double, string>.Success(_state);
        }
    }

    public class Result<T, E>
    {
        public bool IsSuccess { get; }
        public T Value { get; }
        public E Error { get; }
        private Result(bool isSuccess, T value, E error) { IsSuccess = isSuccess; Value = value; Error = error; }
        public static Result<T, E> Success(T value) => new Result<T, E>(true, value, default);
        public static Result<T, E> Failure(E error) => new Result<T, E>(false, default, error);
    }
}
