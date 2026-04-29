defmodule Omni.Concurrency.EOSFaceModel.FittingPipeline do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{jobs: %{}, next_id: 1}, name: __MODULE__)
  end

  def submit_fitting_job(pid, landmarks) do
    GenServer.call(pid, {:submit, landmarks})
  end

  def get_job_status(pid, job_id) do
    GenServer.call(pid, {:status, job_id})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_call({:submit, landmarks}, _from, state) do
    job_id = state.next_id
    
    # Simulate async dispatch
    new_jobs = Map.put(state.jobs, job_id, %{landmarks: landmarks, status: :processing})
    
    # In a real app, this casts to a worker pool.
    # We trigger a delayed message to ourselves to complete the job deterministically
    Process.send_after(self(), {:complete_job, job_id}, 100)

    {:reply, {:ok, job_id}, %{state | jobs: new_jobs, next_id: job_id + 1}}
  end

  @impl true
  def handle_call({:status, job_id}, _from, state) do
    case Map.fetch(state.jobs, job_id) do
      {:ok, job} -> {:reply, {:ok, job.status}, state}
      :error -> {:reply, {:error, "Job not found"}, state}
    end
  end

  @impl true
  def handle_info({:complete_job, job_id}, state) do
    if Map.has_key?(state.jobs, job_id) do
      updated_job = %{state.jobs[job_id] | status: :completed}
      {:noreply, %{state | jobs: Map.put(state.jobs, job_id, updated_job)}}
    else
      {:noreply, state}
    end
  end
end
