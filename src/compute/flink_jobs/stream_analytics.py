from omni.core import Result, Ok, Err

class StreamAnalytics:
    def process_window(self, events: list) -> Result[int, ValueError]:
        if not events:
            return Err(ValueError("No events in window"))
        return Ok(len(events))
