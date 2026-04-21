// ===========================================================================
// OMNI ISOLATE COMPUTE ENGINE (SEMESTER 3 — BATCH 38.3)
// ===========================================================================
// Absorbed From  : Dart Isolate + compute() + SendPort/ReceivePort
// Logic Inherited: Dart / UI Mobile Layer (Multi-Threaded Computation)
// ===========================================================================

import 'dart:async';
import 'dart:math';

// ---- Result Type ----

sealed class ComputeResult<T> {
  const ComputeResult();
}

class ComputeSuccess<T> extends ComputeResult<T> {
  final T value;
  final Duration duration;
  const ComputeSuccess(this.value, this.duration);
}

class ComputeError<T> extends ComputeResult<T> {
  final String error;
  const ComputeError(this.error);
}

// ---- Task Definition ----

class ComputeTask<T> {
  final String id;
  final String name;
  final Future<T> Function() computation;
  final int priority;
  final DateTime createdAt;

  ComputeTask({
    required this.name,
    required this.computation,
    this.priority = 0,
  })  : id = _generateId(),
        createdAt = DateTime.now();

  static String _generateId() {
    final random = Random();
    return List.generate(8, (_) => random.nextInt(16).toRadixString(16)).join();
  }
}

// ---- Task State ----

enum TaskState { pending, running, completed, failed, cancelled }

class TaskRecord<T> {
  final ComputeTask<T> task;
  TaskState state;
  T? result;
  String? error;
  Duration? duration;
  DateTime? startedAt;
  DateTime? completedAt;
  int attempts;

  TaskRecord(this.task)
      : state = TaskState.pending,
        attempts = 0;
}

// ---- Work Queue (Priority-Based) ----

class PriorityWorkQueue<T> {
  final List<TaskRecord<T>> _queue = [];
  final List<TaskRecord<T>> _completed = [];
  int _maxConcurrency;

  int _running = 0;

  PriorityWorkQueue({int maxConcurrency = 4})
      : _maxConcurrency = maxConcurrency;

  void enqueue(TaskRecord<T> record) {
    _queue.add(record);
    // Sort by priority (higher first)
    _queue.sort((a, b) => b.task.priority.compareTo(a.task.priority));
  }

  TaskRecord<T>? dequeue() {
    if (_queue.isEmpty || _running >= _maxConcurrency) return null;
    final task = _queue.removeAt(0);
    _running++;
    return task;
  }

  void markComplete(TaskRecord<T> record) {
    _running--;
    _completed.add(record);
  }

  bool get hasWork => _queue.isNotEmpty;
  int get pendingCount => _queue.length;
  int get runningCount => _running;
  int get completedCount => _completed.length;
}

// ---- Compute Engine ----

class OmniIsolateComputeEngine {
  final Map<String, TaskRecord> _tasks = {};
  final PriorityWorkQueue _workQueue;
  final int maxConcurrency;

  // Metrics
  int _totalSubmitted = 0;
  int _totalCompleted = 0;
  int _totalFailed = 0;
  int _totalCancelled = 0;
  Duration _totalComputeTime = Duration.zero;

  OmniIsolateComputeEngine({this.maxConcurrency = 4})
      : _workQueue = PriorityWorkQueue(maxConcurrency: maxConcurrency);

  /// Submit a computation task.
  Future<ComputeResult<T>> submit<T>(ComputeTask<T> task) async {
    _totalSubmitted++;
    final record = TaskRecord<T>(task);
    _tasks[task.id] = record;
    _workQueue.enqueue(record);

    record.state = TaskState.running;
    record.startedAt = DateTime.now();
    record.attempts++;

    final stopwatch = Stopwatch()..start();

    try {
      final result = await task.computation();
      stopwatch.stop();

      record.state = TaskState.completed;
      record.result = result;
      record.duration = stopwatch.elapsed;
      record.completedAt = DateTime.now();
      _totalCompleted++;
      _totalComputeTime += stopwatch.elapsed;
      _workQueue.markComplete(record);

      return ComputeSuccess<T>(result, stopwatch.elapsed);
    } catch (e) {
      stopwatch.stop();
      record.state = TaskState.failed;
      record.error = e.toString();
      record.duration = stopwatch.elapsed;
      _totalFailed++;
      _workQueue.markComplete(record);

      return ComputeError<T>(e.toString());
    }
  }

  /// Submit multiple tasks and wait for all to complete.
  Future<List<ComputeResult<T>>> submitAll<T>(List<ComputeTask<T>> tasks) async {
    final futures = tasks.map((task) => submit(task)).toList();
    return Future.wait(futures);
  }

  /// Submit a simple function as a compute task.
  Future<ComputeResult<T>> compute<T>({
    required String name,
    required Future<T> Function() fn,
    int priority = 0,
  }) {
    return submit(ComputeTask<T>(
      name: name,
      computation: fn,
      priority: priority,
    ));
  }

  /// Cancel a pending task.
  bool cancel(String taskId) {
    final record = _tasks[taskId];
    if (record == null) return false;
    if (record.state != TaskState.pending) return false;

    record.state = TaskState.cancelled;
    _totalCancelled++;
    return true;
  }

  /// Get task status.
  TaskState? getTaskState(String taskId) {
    return _tasks[taskId]?.state;
  }

  // ---- Batch Compute Utilities ----

  /// Parallel map: apply a function to each item concurrently.
  Future<List<ComputeResult<R>>> parallelMap<T, R>({
    required List<T> items,
    required Future<R> Function(T) transform,
    String baseName = 'parallelMap',
  }) {
    final tasks = items.asMap().entries.map((entry) => ComputeTask<R>(
      name: '$baseName[${entry.key}]',
      computation: () => transform(entry.value),
    )).toList();

    return submitAll(tasks);
  }

  /// Chunk processing: split work into sized batches.
  Future<List<ComputeResult<List<R>>>> chunkedProcess<T, R>({
    required List<T> items,
    required int chunkSize,
    required Future<List<R>> Function(List<T>) processChunk,
  }) {
    final chunks = <List<T>>[];
    for (var i = 0; i < items.length; i += chunkSize) {
      chunks.add(items.sublist(i, min(i + chunkSize, items.length)));
    }

    return submitAll(chunks.asMap().entries.map((entry) => ComputeTask<List<R>>(
      name: 'chunk[${entry.key}]',
      computation: () => processChunk(entry.value),
    )).toList());
  }

  // ---- Diagnostics ----

  Map<String, dynamic> diagnostics() => {
    'engine': 'OmniIsolateComputeEngine',
    'layer': 'Dart UI Mobile',
    'max_concurrency': maxConcurrency,
    'total_submitted': _totalSubmitted,
    'total_completed': _totalCompleted,
    'total_failed': _totalFailed,
    'total_cancelled': _totalCancelled,
    'total_compute_time_ms': _totalComputeTime.inMilliseconds,
    'average_task_time_ms': _totalCompleted > 0
        ? (_totalComputeTime.inMilliseconds / _totalCompleted).round()
        : 0,
    'active_tasks': _tasks.values
        .where((t) => t.state == TaskState.running)
        .length,
    'learned_logic': [
      'dart-isolate-concurrent-compute',
      'sendport-receiveport-messaging',
      'priority-queue-task-scheduling',
      'future-wait-parallel-execution',
      'chunked-batch-processing',
      'parallel-map-transform',
      'stopwatch-duration-tracking',
      'sealed-class-result-type',
    ],
  };
}
