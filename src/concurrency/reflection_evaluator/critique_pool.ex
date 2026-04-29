defmodule Omni.Concurrency.ReflectionEvaluator.CritiquePool do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{active_critiques: 0}, name: __MODULE__)
  end

  def dispatch_critique_task(pid, draft_id) do
    GenServer.call(pid, {:critique, draft_id})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_call({:critique, _id}, _from, state) do
    # Distributed Elixir worker managing background LLM critique instances
    # Allows primary generation threads to offload self-reflection asynchronously
    
    new_count = state.active_critiques + 1
    
    {:reply, :ok, %{state | active_critiques: new_count}}
  end
end
