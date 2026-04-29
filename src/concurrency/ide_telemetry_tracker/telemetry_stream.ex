defmodule Omni.Concurrency.IDETelemetryTracker.TelemetryStream do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{events_streamed: 0}, name: __MODULE__)
  end

  def stream_event(pid, event_payload) do
    GenServer.cast(pid, {:stream, event_payload})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_cast({:stream, _payload}, state) do
    # Distributed Elixir worker buffering and streaming thousands of IDE telemetry events
    # Uses cast for asynchronous "fire and forget" to avoid blocking the client
    
    new_count = state.events_streamed + 1
    
    {:noreply, %{state | events_streamed: new_count}}
  end
end
