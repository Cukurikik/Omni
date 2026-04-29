using System;
using System.Collections.Generic;

namespace Omni.Business.Ray
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

    public enum ResourceType { CPU, GPU, TPU, MemoryIntensive }

    public class RayTask
    {
        public string TaskId { get; set; } = Guid.NewGuid().ToString();
        public ResourceType RequiredResource { get; set; }
        public int Priority { get; set; }
        public string Payload { get; set; } = string.Empty;
    }

    public class TaskRouter
    {
        private readonly Dictionary<ResourceType, string> _resourceQueues;

        public TaskRouter()
        {
            _resourceQueues = new Dictionary<ResourceType, string>
            {
                { ResourceType.CPU, "queue_cpu_general" },
                { ResourceType.GPU, "queue_gpu_compute" },
                { ResourceType.TPU, "queue_tpu_accelerator" },
                { ResourceType.MemoryIntensive, "queue_high_mem" }
            };
        }

        public Result<string, string> RouteTask(RayTask task)
        {
            if (task == null) return Result<string, string>.Failure("Task cannot be null");
            if (string.IsNullOrEmpty(task.Payload)) return Result<string, string>.Failure("Task payload cannot be empty");

            if (_resourceQueues.TryGetValue(task.RequiredResource, out var queueName))
            {
                // In production, this pushes to Redis/RabbitMQ which Ray pulls from
                string routingToken = $"{queueName}::{task.Priority}::{task.TaskId}";
                return Result<string, string>.Success(routingToken);
            }

            return Result<string, string>.Failure($"Unknown resource type: {task.RequiredResource}");
        }
    }
}
