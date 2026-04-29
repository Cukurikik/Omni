defmodule Omni.Concurrency.CleanlabNoise.CleanerPool do
  use GenServer

  def start_link(pool_size) do
    GenServer.start_link(__MODULE__, %{pool_size: pool_size, active: 0, queue: []}, name: __MODULE__)
  end

  def submit_batch(pid, batch_id, size) do
    GenServer.cast(pid, {:clean, batch_id, size})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_cast({:clean, batch_id, size}, state) do
    new_queue = state.queue ++ [{batch_id, size}]
    {:noreply, try_dispatch(%{state | queue: new_queue})}
  end

  defp try_dispatch(state) do
    if state.active < state.pool_size and length(state.queue) > 0 do
      [{batch_id, size} | rest] = state.queue
      
      IO.puts("Cleanlab Worker: Scanning Batch [#{batch_id}] of size #{size} for noise")
      
      # Simulate deterministic processing time proportional to batch size
      Process.send_after(self(), {:done, batch_id}, 10 + round(size * 0.1))
      
      try_dispatch(%{state | queue: rest, active: state.active + 1})
    else
      state
    end
  end

  @impl true
  def handle_info({:done, batch_id}, state) do
    IO.puts("Cleanlab Worker: Batch [#{batch_id}] scan complete.")
    new_state = %{state | active: state.active - 1}
    {:noreply, try_dispatch(new_state)}
  end
end
