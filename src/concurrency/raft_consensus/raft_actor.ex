defmodule Omni.Concurrency.RaftConsensus.RaftActor do
  use GenServer

  def start_link(node_id) do
    GenServer.start_link(__MODULE__, %{
      id: node_id,
      state: :follower,
      current_term: 0,
      voted_for: nil
    }, name: String.to_atom("raft_node_#{node_id}"))
  end

  def receive_heartbeat(pid, leader_term) do
    GenServer.cast(pid, {:heartbeat, leader_term})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_cast({:heartbeat, leader_term}, state) do
    if leader_term >= state.current_term do
      # Valid heartbeat from leader, reset election timer and step down if candidate
      new_state = %{state | state: :follower, current_term: leader_term}
      {:noreply, new_state}
    else
      # Ignore stale leader
      {:noreply, state}
    end
  end
end
