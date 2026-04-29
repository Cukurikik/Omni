// OMNI MOTHER - DIVINE MEMORY INTEGRATION
// OmniFocus GTD Queue (OMNI Zero-Mock Implementation)
// Implements priority queue binary heap for Getting Things Done processing.

using System;
using System.Collections.Generic;

namespace Omni.Compute.OmniFocus
{
    public class Result<T>
    {
        public T Value { get; }
        public string Error { get; }
        public bool IsOk { get; }

        private Result(T val, string err, bool isOk)
        {
            Value = val;
            Error = err;
            IsOk = isOk;
        }

        public static Result<T> Ok(T val) => new Result<T>(val, null, true);
        public static Result<T> Err(string err) => new Result<T>(default(T), err, false);
    }

    public class TaskItem : IComparable<TaskItem>
    {
        public string Id { get; }
        public int Priority { get; } // Lower number = Higher priority
        public long Timestamp { get; }

        public TaskItem(string id, int priority, long timestamp)
        {
            Id = id;
            Priority = priority;
            Timestamp = timestamp;
        }

        public int CompareTo(TaskItem other)
        {
            if (Priority != other.Priority)
            {
                return Priority.CompareTo(other.Priority);
            }
            // FIFO fallback
            return Timestamp.CompareTo(other.Timestamp);
        }
    }

    public class GTDPriorityQueue
    {
        private readonly List<TaskItem> _heap = new List<TaskItem>();

        public void Enqueue(TaskItem item)
        {
            _heap.Add(item);
            HeapifyUp(_heap.Count - 1);
        }

        public Result<TaskItem> Dequeue()
        {
            if (_heap.Count == 0) return Result<TaskItem>.Err("Queue is empty.");

            var root = _heap[0];
            var last = _heap[_heap.Count - 1];
            _heap.RemoveAt(_heap.Count - 1);

            if (_heap.Count > 0)
            {
                _heap[0] = last;
                HeapifyDown(0);
            }

            return Result<TaskItem>.Ok(root);
        }

        private void HeapifyUp(int i)
        {
            while (i > 0)
            {
                int parent = (i - 1) / 2;
                if (_heap[i].CompareTo(_heap[parent]) >= 0) break;

                // Swap
                var temp = _heap[i];
                _heap[i] = _heap[parent];
                _heap[parent] = temp;
                i = parent;
            }
        }

        private void HeapifyDown(int i)
        {
            int lastIndex = _heap.Count - 1;
            while (true)
            {
                int leftChild = 2 * i + 1;
                int rightChild = 2 * i + 2;
                int smallest = i;

                if (leftChild <= lastIndex && _heap[leftChild].CompareTo(_heap[smallest]) < 0)
                    smallest = leftChild;
                if (rightChild <= lastIndex && _heap[rightChild].CompareTo(_heap[smallest]) < 0)
                    smallest = rightChild;

                if (smallest == i) break;

                // Swap
                var temp = _heap[i];
                _heap[i] = _heap[smallest];
                _heap[smallest] = temp;
                i = smallest;
            }
        }
    }
}
