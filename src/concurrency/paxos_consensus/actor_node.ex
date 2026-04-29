defmodule Omni.Concurrency.PaxosConsensus.ActorNode do
  use GenServer

  def start_link(node_id) do
    GenServer.start_link(__MODULE__, %{id: node_id, current_round: 0}, name: String.to_atom("paxos_node_#{node_id}"))
  end

  def propose(pid, round, value) do
    GenServer.cast(pid, {:propose, round, value})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_cast({:propose, round, value}, state) do
    if round > state.current_round do
      # IO.puts("Paxos Node #{state.id}: Promised round #{round} for value #{value}")
      {:noreply, %{state | current_round: round}}
    else
      # IO.puts("Paxos Node #{state.id}: Rejected round #{round} (Current: #{state.current_round})")
      {:noreply, state}
    end
  end
end
