defmodule Omni.Concurrency.DVCVersioning.HashWorkerPool do
  use GenServer

  def start_link(pool_size) do
    GenServer.start_link(__MODULE__, %{pool_size: pool_size, active: 0, queue: []}, name: __MODULE__)
  end

  def hash_file(pid, file_path) do
    GenServer.cast(pid, {:hash, file_path})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_cast({:hash, file_path}, state) do
    new_queue = state.queue ++ [file_path]
    {:noreply, try_dispatch(%{state | queue: new_queue})}
  end

  defp try_dispatch(state) do
    if state.active < state.pool_size and length(state.queue) > 0 do
      [path | rest] = state.queue
      
      IO.puts("DVC Worker: Computing MD5 for [#{path}]")
      
      # Simulate deterministic computation
      Process.send_after(self(), :done, 50)
      
      try_dispatch(%{state | queue: rest, active: state.active + 1})
    else
      state
    end
  end

  @impl true
  def handle_info(:done, state) do
    new_state = %{state | active: state.active - 1}
    {:noreply, try_dispatch(new_state)}
  end
end
