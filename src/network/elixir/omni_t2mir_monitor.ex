defmodule OmniMoE.T2MIRTracker do
  use GenServer

  # OMNI MOTHER: T2MIR RL Trajectory Tracker
  # Collects in-context RL trajectories across the cluster

  def start_link(opts) do
    GenServer.start_link(__MODULE__, :ok, name: __MODULE__)
  end

  @impl true
  def init(:ok) do
    {:ok, []}
  end

  @impl true
  def handle_cast({:record_trajectory, traj}, state) do
    {:noreply, [traj | state]}
  end
end
