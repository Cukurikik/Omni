defmodule Omni.Concurrency.FederatedLearning.RoundCoordinator do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{round_num: 0, active: false}, name: __MODULE__)
  end

  def trigger_round(pid) do
    GenServer.cast(pid, :trigger_round)
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_cast(:trigger_round, state) do
    if state.active do
      # Reject trigger if round already in progress
      {:noreply, state}
    else
      new_round = state.round_num + 1
      
      # Broadcast to clients
      # (Simulated by delayed message to self)
      Process.send_after(self(), :aggregate, 1500)
      
      {:noreply, %{state | round_num: new_round, active: true}}
    end
  end

  @impl true
  def handle_info(:aggregate, state) do
    # Round finishes
    {:noreply, %{state | active: false}}
  end
end
