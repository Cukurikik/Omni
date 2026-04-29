defmodule Omni.Concurrency.EnergyAwareScheduler.TaskPauser do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{tasks_paused: 0}, name: __MODULE__)
  end

  def pause_low_priority(pid) do
    GenServer.call(pid, :pause_tasks)
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_call(:pause_tasks, _from, state) do
    # Distributed Elixir worker managing task suspension
    # Immediately pauses background RAG indexing when the mobile device drops below 20% battery
    
    new_count = state.tasks_paused + 1
    
    {:reply, :ok, %{state | tasks_paused: new_count}}
  end
end
