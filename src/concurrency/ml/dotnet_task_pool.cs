using System;
using System.Collections.Concurrent;
using System.Threading;
using System.Threading.Tasks;

namespace Omni.Concurrency.ML
{
    public class Result<T, E>
    {
        public bool IsSuccess { get; }
        public T Value { get; }
        public E Error { get; }
        private Result(bool isSuccess, T value, E error) { IsSuccess = isSuccess; Value = value; Error = error; }
        public static Result<T, E> Success(T value) => new Result<T, E>(true, value, default!);
        public static Result<T, E> Failure(E error) => new Result<T, E>(false, default!, error);
    }

    public class MLTaskPool : IDisposable
    {
        private readonly BlockingCollection<Func<Task>> _workQueue;
        private readonly CancellationTokenSource _cts;
        private readonly Task[] _workers;

        public MLTaskPool(int workerCount)
        {
            _workQueue = new BlockingCollection<Func<Task>>();
            _cts = new CancellationTokenSource();
            _workers = new Task[workerCount];

            for (int i = 0; i < workerCount; i++)
            {
                _workers[i] = Task.Run(() => WorkerLoop(_cts.Token));
            }
        }

        private async Task WorkerLoop(CancellationToken token)
        {
            try
            {
                foreach (var workItem in _workQueue.GetConsumingEnumerable(token))
                {
                    if (token.IsCancellationRequested) break;
                    try
                    {
                        await workItem();
                    }
                    catch (Exception ex)
                    {
                        // In production OMNI, this is logged to TelemetryStream
                        Console.WriteLine($"Worker caught exception: {ex}");
                    }
                }
            }
            catch (OperationCanceledException)
            {
                // Expected on shutdown
            }
        }

        public Task<Result<T, string>> SubmitAsync<T>(Func<Task<T>> computeFunc)
        {
            var tcs = new TaskCompletionSource<Result<T, string>>();

            _workQueue.Add(async () =>
            {
                try
                {
                    T result = await computeFunc();
                    tcs.SetResult(Result<T, string>.Success(result));
                }
                catch (Exception ex)
                {
                    tcs.SetResult(Result<T, string>.Failure(ex.Message));
                }
            });

            return tcs.Task;
        }

        public void Dispose()
        {
            _cts.Cancel();
            _workQueue.CompleteAdding();
            Task.WaitAll(_workers, TimeSpan.FromSeconds(5));
            _workQueue.Dispose();
            _cts.Dispose();
        }
    }
}
