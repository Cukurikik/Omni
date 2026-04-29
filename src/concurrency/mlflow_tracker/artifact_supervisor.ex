defmodule Omni.Concurrency.MLFlowTracker.ArtifactSupervisor do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{tracking: %{}}, name: __MODULE__)
  end

  def track_artifact(pid, run_id, artifact_path) do
    GenServer.cast(pid, {:track, run_id, artifact_path})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_cast({:track, run_id, artifact_path}, state) do
    current_artifacts = Map.get(state.tracking, run_id, [])
    new_artifacts = current_artifacts ++ [artifact_path]
    
    IO.puts("MLFlow: Tracking artifact [#{artifact_path}] for Run [#{run_id}]")
    
    new_state = %{state | tracking: Map.put(state.tracking, run_id, new_artifacts)}
    {:noreply, new_state}
  end
end
