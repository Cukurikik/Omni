defmodule Omni.Concurrency.CircuitBreaker.Broadcaster do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{state: "CLOSED"}, name: __MODULE__)
  end

  def broadcast_state(pid, new_state) do
    GenServer.cast(pid, {:broadcast, new_state})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_cast({:broadcast, new_state}, state) do
    if state.state != new_state do
      # IO.puts("Breaker Broadcaster: Notifying cluster of state change -> #{new_state}")
      {:noreply, %{state | state: new_state}}
    else
      {:noreply, state}
    end
  end
end
