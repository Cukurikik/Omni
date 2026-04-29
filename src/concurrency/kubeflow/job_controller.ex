defmodule Omni.Kubeflow.JobController do
  @moduledoc """
  OMNI KUBEFLOW: Elixir Kubernetes Job Controller
  Monitors K8s Pod statuses for ML workflows and triggers downstream actions based on state changes.
  Source: kubeflow/pipelines
  """
  use GenServer
  require Logger

  # --- API ---
  def start_link(k8s_client_config) do
    GenServer.start_link(__MODULE__, k8s_client_config, name: __MODULE__)
  end

  def watch_job(job_id) do
    GenServer.cast(__MODULE__, {:watch, job_id})
  end

  # --- Callbacks ---
  @impl true
  def init(_config) do
    # Simulated connection setup to K8s API
    Logger.info("Kubeflow Job Controller connected to K8s API.")
    {:ok, %{watched_jobs: MapSet.new()}}
  end

  @impl true
  def handle_cast({:watch, job_id}, state) do
    new_jobs = MapSet.put(state.watched_jobs, job_id)
    
    # Spawn a dedicated watcher process per job
    Task.Supervisor.async_nolink(Omni.Kubeflow.WatcherSupervisor, fn ->
      poll_k8s_api(job_id)
    end)
    
    {:noreply, %{state | watched_jobs: new_jobs}}
  end

  @impl true
  def handle_info({ref, {:job_completed, job_id, final_status}}, state) do
    Process.demonitor(ref, [:flush])
    Logger.info("Job #{job_id} terminated with status: #{final_status}")
    
    # Here we would trigger an event on Kafka or via HTTP webhook
    # Omni.Events.publish("kubeflow.job.completed", %{id: job_id, status: final_status})
    
    new_jobs = MapSet.delete(state.watched_jobs, job_id)
    {:noreply, %{state | watched_jobs: new_jobs}}
  end

  @impl true
  def handle_info({:DOWN, _ref, :process, _pid, _reason}, state) do
    {:noreply, state}
  end

  # --- Internal Worker ---
  defp poll_k8s_api(job_id) do
    # Simulate K8s long-polling or informer watch
    Logger.debug("Watching job: #{job_id}")
    :timer.sleep(2000) # Simulate time passing
    
    # Simulated successful completion
    {:job_completed, job_id, "Succeeded"}
  end
end
