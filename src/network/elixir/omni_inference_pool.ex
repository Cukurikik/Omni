# OMNI Concurrency Layer — Elixir GenServer for Model Inference Pool
# Fault-tolerant distributed inference with OTP supervision.

defmodule Omni.Inference.WorkerPool do
  @moduledoc """
  OTP-supervised inference worker pool for transformer model serving.
  Distributes inference requests across multiple workers with backpressure.
  """

  use Supervisor

  def start_link(opts) do
    pool_size = Keyword.get(opts, :pool_size, System.schedulers_online())
    model_path = Keyword.get(opts, :model_path, "models/omni-7b")
    Supervisor.start_link(__MODULE__, {pool_size, model_path}, name: __MODULE__)
  end

  @impl true
  def init({pool_size, model_path}) do
    children =
      for i <- 1..pool_size do
        Supervisor.child_spec(
          {Omni.Inference.Worker, [id: i, model_path: model_path]},
          id: {Omni.Inference.Worker, i}
        )
      end

    children = [{Omni.Inference.Router, pool_size: pool_size} | children]
    Supervisor.init(children, strategy: :one_for_one, max_restarts: 10, max_seconds: 60)
  end
end

defmodule Omni.Inference.Worker do
  @moduledoc "Single inference worker GenServer."
  use GenServer
  require Logger

  defstruct [:id, :model_path, :model_loaded, :requests_served, :total_latency_ms]

  def start_link(opts) do
    id = Keyword.fetch!(opts, :id)
    GenServer.start_link(__MODULE__, opts, name: via(id))
  end

  defp via(id), do: {:via, Registry, {Omni.Inference.Registry, {:worker, id}}}

  @impl true
  def init(opts) do
    state = %__MODULE__{
      id: Keyword.fetch!(opts, :id),
      model_path: Keyword.get(opts, :model_path, "models/default"),
      model_loaded: false,
      requests_served: 0,
      total_latency_ms: 0.0
    }
    {:ok, state, {:continue, :load_model}}
  end

  @impl true
  def handle_continue(:load_model, state) do
    Logger.info("Worker #{state.id}: Loading model from #{state.model_path}")
    # In production, this would load the actual model weights via NIF/Port
    Process.sleep(100)  # Simulate model loading
    {:noreply, %{state | model_loaded: true}}
  end

  @impl true
  def handle_call({:infer, request}, _from, %{model_loaded: true} = state) do
    start_time = System.monotonic_time(:millisecond)

    # Production inference would call NIF here
    result = %{
      request_id: request.id,
      generated_text: process_request(request),
      tokens_generated: 128,
      model_id: state.id
    }

    latency = System.monotonic_time(:millisecond) - start_time
    new_state = %{state |
      requests_served: state.requests_served + 1,
      total_latency_ms: state.total_latency_ms + latency
    }

    {:reply, {:ok, result}, new_state}
  end

  def handle_call({:infer, _request}, _from, %{model_loaded: false} = state) do
    {:reply, {:error, :model_not_loaded}, state}
  end

  @impl true
  def handle_call(:stats, _from, state) do
    avg_latency = if state.requests_served > 0,
      do: state.total_latency_ms / state.requests_served,
      else: 0.0

    stats = %{
      worker_id: state.id,
      requests_served: state.requests_served,
      avg_latency_ms: Float.round(avg_latency, 2),
      model_loaded: state.model_loaded
    }
    {:reply, stats, state}
  end

  defp process_request(request) do
    # Placeholder for actual NIF-based inference
    "Generated response for: #{String.slice(request.text || "", 0..50)}"
  end
end

defmodule Omni.Inference.Router do
  @moduledoc "Round-robin request router across inference workers."
  use GenServer

  defstruct [:pool_size, :current_index, :total_routed]

  def start_link(opts) do
    GenServer.start_link(__MODULE__, opts, name: __MODULE__)
  end

  @impl true
  def init(opts) do
    {:ok, %__MODULE__{
      pool_size: Keyword.fetch!(opts, :pool_size),
      current_index: 1,
      total_routed: 0
    }}
  end

  def infer(request) do
    GenServer.call(__MODULE__, {:route, request}, 30_000)
  end

  @impl true
  def handle_call({:route, request}, _from, state) do
    worker_name = {:via, Registry, {Omni.Inference.Registry, {:worker, state.current_index}}}

    result = try do
      GenServer.call(worker_name, {:infer, request}, 25_000)
    catch
      :exit, _ -> {:error, :worker_unavailable}
    end

    next_index = rem(state.current_index, state.pool_size) + 1
    {:reply, result, %{state | current_index: next_index, total_routed: state.total_routed + 1}}
  end
end
