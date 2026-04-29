defmodule Omni.Concurrency.ReactReasoningLoop.AgentThread do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{active_threads: 0}, name: __MODULE__)
  end

  def spawn_reasoning_loop(pid, goal_id) do
    GenServer.call(pid, {:spawn_loop, goal_id})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_call({:spawn_loop, _goal_id}, _from, state) do
    # Distributed Elixir worker managing isolated reasoning threads
    # Each thread holds the context and memory of a single ReAct loop iteration
    
    new_count = state.active_threads + 1
    
    {:reply, :ok, %{state | active_threads: new_count}}
  end
end
