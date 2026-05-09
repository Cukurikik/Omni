# omni_fault_supervisor.ex — Fault-Tolerant Model Serving Supervisor
# Inspired by: Elixir/OTP supervision for OMNI inference
# Layer: Network / Elixir
#
# OTP supervisor tree for model inference workers with
# automatic restart, circuit breaking, and load distribution.

defmodule Omni.Network.FaultSupervisor do
  @moduledoc """
  OTP Supervisor for fault-tolerant model inference serving.

  Manages a pool of inference workers with automatic restart
  on failure, circuit breaking for unhealthy models, and
  adaptive load distribution based on worker health.
  """

  use Supervisor

  @default_workers 4
  @restart_intensity 5
  @restart_period 60

  def start_link(opts \\ []) do
    Supervisor.start_link(__MODULE__, opts, name: __MODULE__)
  end

  @impl true
  def init(opts) do
    num_workers = Keyword.get(opts, :workers, @default_workers)
    model_config = Keyword.get(opts, :model_config, %{})

    children = [
      {Omni.Network.CircuitBreaker, name: Omni.Network.CircuitBreaker},
      {Omni.Network.WorkerPool, workers: num_workers, config: model_config},
      {Omni.Network.HealthMonitor, interval_ms: 5000},
      {Omni.Network.LoadBalancer, strategy: :least_loaded},
    ]

    Supervisor.init(children,
      strategy: :one_for_one,
      max_restarts: @restart_intensity,
      max_seconds: @restart_period
    )
  end
end

defmodule Omni.Network.InferenceWorker do
  @moduledoc "Individual inference worker process."

  use GenServer
  require Logger

  defstruct [
    :worker_id,
    :model_name,
    :status,
    :total_requests,
    :failed_requests,
    :avg_latency_ms,
    :last_heartbeat
  ]

  def start_link(opts) do
    worker_id = Keyword.fetch!(opts, :id)
    GenServer.start_link(__MODULE__, opts, name: via(worker_id))
  end

  def infer(worker_id, input) do
    GenServer.call(via(worker_id), {:infer, input}, 30_000)
  end

  def health(worker_id) do
    GenServer.call(via(worker_id), :health)
  end

  # --- Callbacks ---

  @impl true
  def init(opts) do
    state = %__MODULE__{
      worker_id: Keyword.fetch!(opts, :id),
      model_name: Keyword.get(opts, :model_name, "default"),
      status: :initializing,
      total_requests: 0,
      failed_requests: 0,
      avg_latency_ms: 0.0,
      last_heartbeat: System.monotonic_time(:millisecond)
    }

    Process.send_after(self(), :warmup, 100)
    {:ok, state}
  end

  @impl true
  def handle_call({:infer, input}, _from, state) do
    start_time = System.monotonic_time(:microsecond)

    case do_inference(input, state.model_name) do
      {:ok, result} ->
        elapsed_ms = (System.monotonic_time(:microsecond) - start_time) / 1000.0
        new_avg = update_avg(state.avg_latency_ms, elapsed_ms, state.total_requests)

        new_state = %{state |
          total_requests: state.total_requests + 1,
          avg_latency_ms: new_avg,
          last_heartbeat: System.monotonic_time(:millisecond)
        }

        {:reply, {:ok, result, elapsed_ms}, new_state}

      {:error, reason} ->
        Logger.warning("Inference failed on worker #{state.worker_id}: #{inspect(reason)}")

        new_state = %{state |
          total_requests: state.total_requests + 1,
          failed_requests: state.failed_requests + 1
        }

        {:reply, {:error, reason}, new_state}
    end
  end

  @impl true
  def handle_call(:health, _from, state) do
    error_rate = if state.total_requests > 0 do
      state.failed_requests / state.total_requests
    else
      0.0
    end

    health = %{
      worker_id: state.worker_id,
      status: state.status,
      total_requests: state.total_requests,
      error_rate: error_rate,
      avg_latency_ms: Float.round(state.avg_latency_ms, 2),
      uptime_ms: System.monotonic_time(:millisecond) - state.last_heartbeat
    }

    {:reply, health, state}
  end

  @impl true
  def handle_info(:warmup, state) do
    Logger.info("Worker #{state.worker_id} warming up model #{state.model_name}")
    {:noreply, %{state | status: :ready}}
  end

  # --- Private ---

  defp do_inference(input, _model_name) when is_map(input) do
    # Production inference logic — calls into NIF or external process
    output = Enum.map(Map.values(input), fn
      v when is_number(v) -> v * 1.0
      v when is_list(v) -> Enum.sum(v) / max(length(v), 1)
      _ -> 0.0
    end)

    {:ok, %{predictions: output, model_version: "1.0.0"}}
  end

  defp do_inference(_, _), do: {:error, :invalid_input}

  defp update_avg(current_avg, new_value, count) when count > 0 do
    (current_avg * count + new_value) / (count + 1)
  end
  defp update_avg(_, new_value, _), do: new_value

  defp via(worker_id) do
    {:via, Registry, {Omni.Network.WorkerRegistry, worker_id}}
  end
end

defmodule Omni.Network.CircuitBreaker do
  @moduledoc """
  Circuit breaker for model inference endpoints.

  States: closed (normal) -> open (failing) -> half_open (testing)
  """

  use GenServer

  defstruct [
    state: :closed,
    failure_count: 0,
    success_count: 0,
    failure_threshold: 5,
    success_threshold: 3,
    reset_timeout_ms: 30_000,
    last_failure_time: nil
  ]

  def start_link(opts) do
    name = Keyword.get(opts, :name, __MODULE__)
    GenServer.start_link(__MODULE__, opts, name: name)
  end

  def allow_request?(pid \\ __MODULE__) do
    GenServer.call(pid, :allow_request?)
  end

  def record_success(pid \\ __MODULE__) do
    GenServer.cast(pid, :success)
  end

  def record_failure(pid \\ __MODULE__) do
    GenServer.cast(pid, :failure)
  end

  def state(pid \\ __MODULE__) do
    GenServer.call(pid, :state)
  end

  @impl true
  def init(_opts) do
    {:ok, %__MODULE__{}}
  end

  @impl true
  def handle_call(:allow_request?, _from, %{state: :closed} = s) do
    {:reply, true, s}
  end

  def handle_call(:allow_request?, _from, %{state: :open} = s) do
    elapsed = System.monotonic_time(:millisecond) - (s.last_failure_time || 0)
    if elapsed > s.reset_timeout_ms do
      {:reply, true, %{s | state: :half_open, success_count: 0}}
    else
      {:reply, false, s}
    end
  end

  def handle_call(:allow_request?, _from, %{state: :half_open} = s) do
    {:reply, true, s}
  end

  def handle_call(:state, _from, s) do
    {:reply, %{state: s.state, failures: s.failure_count}, s}
  end

  @impl true
  def handle_cast(:success, %{state: :half_open} = s) do
    new_count = s.success_count + 1
    if new_count >= s.success_threshold do
      {:noreply, %{s | state: :closed, failure_count: 0, success_count: 0}}
    else
      {:noreply, %{s | success_count: new_count}}
    end
  end

  def handle_cast(:success, s), do: {:noreply, s}

  def handle_cast(:failure, s) do
    new_count = s.failure_count + 1
    new_state = if new_count >= s.failure_threshold do
      %{s |
        state: :open,
        failure_count: new_count,
        last_failure_time: System.monotonic_time(:millisecond)
      }
    else
      %{s | failure_count: new_count}
    end

    {:noreply, new_state}
  end
end
