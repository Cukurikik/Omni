import gleam/string
import gleam/list

pub type LogLevel {
  Info
  Warning
  Error
  Critical
}

pub type LogEntry {
  LogEntry(level: LogLevel, message: String)
}

pub fn parse_log_stream(logs: List(String)) -> List(LogEntry) {
  logs
  |> list.map(fn(log) {
    case string.starts_with(log, "[ERROR]") {
      True -> LogEntry(Error, log)
      False -> LogEntry(Info, log)
    }
  })
}
