defmodule Omni.Concurrency.KongGateway.RequestSupervisor do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{active_requests: 0}, name: __MODULE__)
  end

  def process_request(pid, req_id) do
    GenServer.cast(pid, {:process, req_id})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_cast({:process, req_id}, state) do
    # IO.puts("Kong Supervisor: Starting plugin pipeline for Request [#{req_id}]")
    
    # Simulate pipeline execution across multiple plugins deterministically
    Process.send_after(self(), :pipeline_done, 15)
    
    {:noreply, %{state | active_requests: state.active_requests + 1}}
  end

  @impl true
  def handle_info(:pipeline_done, state) do
    new_active = max(0, state.active_requests - 1)
    # IO.puts("Kong Supervisor: Pipeline complete. Active requests: #{new_active}")
    {:noreply, %{state | active_requests: new_active}}
  end
end
