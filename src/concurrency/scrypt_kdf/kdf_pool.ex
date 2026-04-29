defmodule Omni.Concurrency.ScryptKDF.KDFPool do
  use GenServer

  def start_link(pool_size) do
    GenServer.start_link(__MODULE__, %{pool_size: pool_size, active: 0, queue: []}, name: __MODULE__)
  end

  def derive_key(pid, req_id, n_cost) do
    GenServer.cast(pid, {:derive, req_id, n_cost})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_cast({:derive, req_id, n_cost}, state) do
    new_queue = state.queue ++ [{req_id, n_cost}]
    {:noreply, try_dispatch(%{state | queue: new_queue})}
  end

  defp try_dispatch(state) do
    if state.active < state.pool_size and length(state.queue) > 0 do
      [{req_id, n_cost} | rest] = state.queue
      
      # Simulate memory-hard delay (N scaled)
      delay = trunc(n_cost / 100)
      Process.send_after(self(), {:done, req_id}, max(10, delay))
      
      try_dispatch(%{state | queue: rest, active: state.active + 1})
    else
      state
    end
  end

  @impl true
  def handle_info({:done, req_id}, state) do
    new_state = %{state | active: state.active - 1}
    {:noreply, try_dispatch(new_state)}
  end
end
