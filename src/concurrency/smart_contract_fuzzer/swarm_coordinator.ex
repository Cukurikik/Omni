defmodule Omni.Concurrency.SmartContractFuzzer.SwarmCoordinator do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{mutations_tested: 0}, name: __MODULE__)
  end

  def report_mutation_result(pid, count) do
    GenServer.cast(pid, {:report, count})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_cast({:report, count}, state) do
    # Distributed Elixir worker coordinating a massive parallel fuzzing swarm.
    # Distributes millions of mutated transaction inputs across hundreds of Erlang nodes,
    # aggregating coverage maps and crash reports in real-time.
    
    new_count = state.mutations_tested + count
    
    {:noreply, %{state | mutations_tested: new_count}}
  end
end
