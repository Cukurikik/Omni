defmodule Omni.Concurrency.Optimization.HyperTuner do
  use GenServer
  require Logger

  # Monadic-style result struct
  defmodule Result do
    defsturct [:ok, :error]
    
    def ok(value), do: %Result{ok: value, error: nil}
    def error(reason), do: %Result{ok: nil, error: reason}
    def is_ok?(%Result{error: nil}), do: true
    def is_ok?(_), do: false
  end

  # --- Client API ---

  def start_link(opts \\ []) do
    GenServer.start_link(__MODULE__, opts, name: __MODULE__)
  end

  def submit_grid(pid, param_grid) do
    GenServer.call(pid, {:submit_grid, param_grid})
  end

  def get_best_params(pid) do
    GenServer.call(pid, :get_best)
  end

  # --- Server Callbacks ---

  @impl true
  def init(_opts) do
    state = %{
      queue: [],
      in_flight: %{},
      results: [],
      best_loss: :infinity,
      best_params: nil
    }
    {:ok, state}
  end

  @impl true
  def handle_call({:submit_grid, param_grid}, _from, state) do
    if is_list(param_grid) do
      new_state = %{state | queue: state.queue ++ param_grid}
      
      # Spawn worker evaluation
      Enum.each(1..min(4, length(param_grid)), fn _ -> 
        send(self(), :dispatch_worker)
      end)
      
      {:reply, Result.ok(:submitted), new_state}
    else
      {:reply, Result.error("param_grid must be a list"), state}
    end
  end

  @impl true
  def handle_call(:get_best, _from, state) do
    if state.best_params != nil do
      {:reply, Result.ok(%{params: state.best_params, loss: state.best_loss}), state}
    else
      {:reply, Result.error("No evaluations completed yet"), state}
    end
  end

  @impl true
  def handle_info(:dispatch_worker, %{queue: [params | rest]} = state) do
    task = Task.async(fn -> 
      # Simulate objective function call (Python FFI bridging would occur here)
      # Simulating a loss based on param mock values for structure
      Process.sleep(100) 
      loss = 1.0 / (Map.get(params, :lr, 0.01) + 1.0)
      {params, loss}
    end)
    
    new_in_flight = Map.put(state.in_flight, task.ref, params)
    {:noreply, %{state | queue: rest, in_flight: new_in_flight}}
  end

  @impl true
  def handle_info(:dispatch_worker, state) do
    {:noreply, state} # Queue empty
  end

  @impl true
  def handle_info({ref, {params, loss}}, state) do
    # Task success
    Process.demonitor(ref, [:flush])
    new_in_flight = Map.delete(state.in_flight, ref)
    new_results = [{params, loss} | state.results]
    
    new_state = if loss < state.best_loss do
      %{state | in_flight: new_in_flight, results: new_results, best_loss: loss, best_params: params}
    else
      %{state | in_flight: new_in_flight, results: new_results}
    end
    
    send(self(), :dispatch_worker) # Keep processing queue
    {:noreply, new_state}
  end
  
  @impl true
  def handle_info({:DOWN, ref, :process, _pid, _reason}, state) do
    Logger.error("Worker task failed")
    # Fault tolerance: requeue failed params
    failed_params = Map.get(state.in_flight, ref)
    new_in_flight = Map.delete(state.in_flight, ref)
    
    new_state = if failed_params do
       %{state | queue: [failed_params | state.queue], in_flight: new_in_flight}
    else
       %{state | in_flight: new_in_flight}
    end
    
    send(self(), :dispatch_worker)
    {:noreply, new_state}
  end
end
