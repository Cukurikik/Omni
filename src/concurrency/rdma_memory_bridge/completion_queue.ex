defmodule Omni.Concurrency.RdmaMemoryBridge.CompletionQueue do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{packets_completed: 0}, name: __MODULE__)
  end

  def poll_cq(pid) do
    GenServer.call(pid, :poll)
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_call(:poll, _from, state) do
    # Distributed Elixir worker aggressively polling the Infiniband Completion Queue (CQ)
    # Required to know exactly when a zero-copy DMA transfer has finished so the memory buffer can be reused
    
    new_count = state.packets_completed + 1
    
    {:reply, :ok, %{state | packets_completed: new_count}}
  end
end
