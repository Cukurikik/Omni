defmodule Omni.Concurrency.RL.ActorCriticSync do
  @moduledoc """
  OMNI RL - Actor-Critic Synchronization Worker
  Elixir OTP Process for coordinating A3C (Asynchronous Advantage Actor-Critic) updates.
  """
  use GenServer

  # API
  def start_link(global_pid) do
    GenServer.start_link(__MODULE__, global_pid, name: __MODULE__)
  end

  def push_gradients(gradients) do
    GenServer.cast(__MODULE__, {:push_gradients, gradients})
  end

  def pull_weights do
    GenServer.call(__MODULE__, :pull_weights)
  end

  # Callbacks
  @impl true
  def init(global_pid) do
    {:ok, %{global_pid: global_pid, local_step: 0, sync_interval: 10}}
  end

  @impl true
  def handle_cast({:push_gradients, gradients}, state) do
    # Forward gradients to global parameter server
    # Expected Monadic interaction: if global_pid is down, don't crash, queue or drop
    try do
      GenServer.cast(state.global_pid, {:apply_gradients, gradients})
      new_step = state.local_step + 1
      
      if rem(new_step, state.sync_interval) == 0 do
        send(self(), :trigger_pull)
      end
      
      {:noreply, %{state | local_step: new_step}}
    rescue
      e ->
        IO.puts("Failed to push gradients to global server: #{inspect(e)}")
        {:noreply, state}
    end
  end

  @impl true
  def handle_call(:pull_weights, _from, state) do
    try do
      weights = GenServer.call(state.global_pid, :get_weights, 5000)
      {:reply, {:ok, weights}, state}
    rescue
      e ->
        {:reply, {:error, "Sync failed: #{inspect(e)}"}, state}
    end
  end

  @impl true
  def handle_info(:trigger_pull, state) do
    # Internal trigger to sync local weights from global
    try do
      # In a real setup, this might update a local ETS table
      _weights = GenServer.call(state.global_pid, :get_weights, 5000)
      {:noreply, state}
    rescue
      _ -> {:noreply, state}
    end
  end
end
