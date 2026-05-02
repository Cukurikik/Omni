// @omni-domain Concurrency Layer (BabyAGI)
// @omni-source yoheinakajima/babyagi
// @omni-description BabyAGI Event Loop mimicking autonomous task creation and execution.
// @omni-requirement zero-mock, monadic-error

import gleam/list
import gleam/result

pub type Task {
  Task(id: String, name: String, status: String)
}

pub type BabyAgiError {
  EmptyQueue
  InvalidTask
}

pub type EventLoop {
  EventLoop(tasks: List(Task), completed: List(Task))
}

pub fn new_loop() -> EventLoop {
  EventLoop([], [])
}

pub fn add_task(loop: EventLoop, task: Task) -> Result(EventLoop, BabyAgiError) {
  case task.name {
    "" -> Error(InvalidTask)
    _ -> Ok(EventLoop([task, ..loop.tasks], loop.completed))
  }
}

pub fn execute_next(loop: EventLoop) -> Result(EventLoop, BabyAgiError) {
  case loop.tasks {
    [] -> Error(EmptyQueue)
    [task, ..rest] -> {
      let completed_task = Task(..task, status: "completed")
      Ok(EventLoop(rest, [completed_task, ..loop.completed]))
    }
  }
}

pub fn get_pending_count(loop: EventLoop) -> Int {
  list.length(loop.tasks)
}
