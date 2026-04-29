defmodule Omni.Concurrency.Argon2Hasher.HashPool do
  use GenServer

  def start_link(pool_size) do
    GenServer.start_link(__MODULE__, %{pool_size: pool_size, active: 0, queue: []}, name: __MODULE__)
  end

  def compute_hash(pid, user_id, password_ref) do
    GenServer.cast(pid, {:hash, user_id, password_ref})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_cast({:hash, user_id, password_ref}, state) do
    new_queue = state.queue ++ [{user_id, password_ref}]
    {:noreply, try_dispatch(%{state | queue: new_queue})}
  end

  defp try_dispatch(state) do
    if state.active < state.pool_size and length(state.queue) > 0 do
      [{user_id, _ref} | rest] = state.queue
      
      IO.puts("Argon2 Worker: Hashing password for User [#{user_id}]...")
      
      # Simulate heavy memory-hard hashing delay deterministically
      Process.send_after(self(), {:done, user_id}, 250)
      
      try_dispatch(%{state | queue: rest, active: state.active + 1})
    else
      state
    end
  end

  @impl true
  def handle_info({:done, user_id}, state) do
    IO.puts("Argon2 Worker: Hash complete for User [#{user_id}].")
    new_state = %{state | active: state.active - 1}
    {:noreply, try_dispatch(new_state)}
  end
end
