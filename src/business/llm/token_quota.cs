using System;
using System.Threading;

namespace Omni.Business.LLM
{
    public class Result<T, E>
    {
        public bool IsSuccess { get; }
        public T Value { get; }
        public E Error { get; }

        private Result(bool isSuccess, T value, E error)
        {
            IsSuccess = isSuccess;
            Value = value;
            Error = error;
        }

        public static Result<T, E> Success(T value) => new Result<T, E>(true, value, default!);
        public static Result<T, E> Failure(E error) => new Result<T, E>(false, default!, error);
    }

    public enum QuotaError
    {
        None,
        QuotaExceeded,
        InvalidAmount,
        AccountSuspended
    }

    public class TokenQuotaManager
    {
        private long _maxTokens;
        private long _consumedTokens;
        private int _isSuspended; // 0 = false, 1 = true

        public TokenQuotaManager(long maxTokens)
        {
            _maxTokens = maxTokens;
            _consumedTokens = 0;
            _isSuspended = 0;
        }

        public Result<long, QuotaError> ConsumeTokens(long count)
        {
            if (count <= 0)
                return Result<long, QuotaError>.Failure(QuotaError.InvalidAmount);

            if (Interlocked.CompareExchange(ref _isSuspended, 0, 0) == 1)
                return Result<long, QuotaError>.Failure(QuotaError.AccountSuspended);

            long initial, computed;
            do
            {
                initial = Interlocked.Read(ref _consumedTokens);
                if (initial + count > _maxTokens)
                {
                    return Result<long, QuotaError>.Failure(QuotaError.QuotaExceeded);
                }
                computed = initial + count;
            } 
            while (Interlocked.CompareExchange(ref _consumedTokens, computed, initial) != initial);

            return Result<long, QuotaError>.Success(computed);
        }

        public Result<bool, QuotaError> SuspendAccount()
        {
            Interlocked.Exchange(ref _isSuspended, 1);
            return Result<bool, QuotaError>.Success(true);
        }

        public Result<long, QuotaError> GetRemainingQuota()
        {
            long consumed = Interlocked.Read(ref _consumedTokens);
            return Result<long, QuotaError>.Success(_maxTokens - consumed);
        }
    }
}
