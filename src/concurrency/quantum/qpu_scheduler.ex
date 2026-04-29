defmodule Omni.Concurrency.Quantum.QPUScheduler do
  @moduledoc """
  OTP Actor for scheduling tasks on QPU hardware resources with strict monadic error handling.
  """
  use GenServer

  # State struct
  defmodule State do
    defstruct queue: [], running_jobs: %{}, available_qpus: 4
  end

  def start_link(opts \\ []) do
    GenServer.start_link(__MODULE__, %State{}, name: __MODULE__)
  end

  def submit_job(job_id, circuit_data) do
    if is_nil(job_id) or is_nil(circuit_data) do
      {:error, :invalid_payload}
    else
      GenServer.call(__MODULE__, {:submit, job_id, circuit_data})
    end
  end

  def get_status(job_id) do
    GenServer.call(__MODULE__, {:status, job_id})
  end

  def complete_job(job_id, result) do
    GenServer.cast(__MODULE__, {:complete, job_id, result})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_call({:submit, job_id, circuit_data}, _from, state) do
    if Map.has_key?(state.running_jobs, job_id) or Enum.any?(state.queue, fn {id, _} -> id == job_id end) do
      {:reply, {:error, :duplicate_job}, state}
    else
      new_state = schedule_jobs(%{state | queue: state.queue ++ [{job_id, circuit_data}]})
      {:reply, {:ok, :submitted}, new_state}
    end
  end

  @impl true
  def handle_call({:status, job_id}, _from, state) do
    cond do
      Map.has_key?(state.running_jobs, job_id) ->
        {:reply, {:ok, :running}, state}
      Enum.any?(state.queue, fn {id, _} -> id == job_id end) ->
        {:reply, {:ok, :queued}, state}
      true ->
        {:reply, {:error, :not_found}, state}
    end
  end

  @impl true
  def handle_cast({:complete, job_id, _result}, state) do
    if Map.has_key?(state.running_jobs, job_id) do
      new_running = Map.delete(state.running_jobs, job_id)
      new_state = schedule_jobs(%{state | running_jobs: new_running, available_qpus: state.available_qpus + 1})
      {:noreply, new_state}
    else
      {:noreply, state}
    end
  end

  defp schedule_jobs(state) do
    cond do
      state.available_qpus > 0 and length(state.queue) > 0 ->
        [{job_id, _data} | rest_queue] = state.queue
        # Simulating dispatch to hardware
        Process.send_after(self(), {:internal_complete, job_id}, 100)
        new_running = Map.put(state.running_jobs, job_id, :active)
        schedule_jobs(%{state | queue: rest_queue, running_jobs: new_running, available_qpus: state.available_qpus - 1})
      true ->
        state
    end
  end

  @impl true
  def handle_info({:internal_complete, job_id}, state) do
    complete_job(job_id, %{fidelity: 0.99})
    {:noreply, state}
  end
end
