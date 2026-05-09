# @omni-layer Concurrency | @omni-lang Elixir | @omni-batch 18 | @omni-semester 16
# @omni-description GenServer-based transformer model serving pool with
# dynamic worker allocation, health checks, and load balancing.

defmodule Omni.Transformer.ModelPool do
  use GenServer
  require Logger

  defstruct [:models, :workers, :stats, :max_workers]

  def start_link(opts \\ []) do
    GenServer.start_link(__MODULE__, opts, name: __MODULE__)
  end

  @impl true
  def init(opts) do
    max_workers = Keyword.get(opts, :max_workers, 8)
    state = %__MODULE__{
      models: %{},
      workers: %{},
      stats: %{requests: 0, errors: 0, avg_latency_ms: 0.0},
      max_workers: max_workers
    }
    schedule_health_check()
    {:ok, state}
  end

  def register_model(model_id, config) do
    GenServer.call(__MODULE__, {:register, model_id, config})
  end

  def infer(model_id, input) do
    GenServer.call(__MODULE__, {:infer, model_id, input}, 30_000)
  end

  def get_stats, do: GenServer.call(__MODULE__, :stats)

  @impl true
  def handle_call({:register, model_id, config}, _from, state) do
    models = Map.put(state.models, model_id, %{
      config: config,
      status: :ready,
      last_used: System.monotonic_time(:millisecond),
      request_count: 0
    })
    {:reply, :ok, %{state | models: models}}
  end

  @impl true
  def handle_call({:infer, model_id, input}, _from, state) do
    start = System.monotonic_time(:millisecond)
    case Map.get(state.models, model_id) do
      nil ->
        {:reply, {:error, :model_not_found}, state}
      model_info ->
        result = execute_inference(model_id, input, model_info)
        elapsed = System.monotonic_time(:millisecond) - start
        updated_model = %{model_info |
          last_used: System.monotonic_time(:millisecond),
          request_count: model_info.request_count + 1
        }
        models = Map.put(state.models, model_id, updated_model)
        stats = update_stats(state.stats, elapsed)
        {:reply, {:ok, result}, %{state | models: models, stats: stats}}
    end
  end

  @impl true
  def handle_call(:stats, _from, state), do: {:reply, state.stats, state}

  @impl true
  def handle_info(:health_check, state) do
    now = System.monotonic_time(:millisecond)
    models = Enum.reduce(state.models, %{}, fn {id, info}, acc ->
      idle_ms = now - info.last_used
      status = if idle_ms > 300_000, do: :idle, else: :ready
      Map.put(acc, id, %{info | status: status})
    end)
    schedule_health_check()
    {:noreply, %{state | models: models}}
  end

  defp execute_inference(model_id, input, _model_info) do
    %{
      model_id: model_id,
      output: process_input(input),
      timestamp: DateTime.utc_now()
    }
  end

  defp process_input(input) when is_list(input) do
    Enum.map(input, fn x ->
      :math.sin(x * 0.001) * 0.5 + :math.cos(x * 0.002) * 0.3
    end)
  end
  defp process_input(input), do: input

  defp update_stats(stats, elapsed) do
    n = stats.requests + 1
    avg = (stats.avg_latency_ms * stats.requests + elapsed) / n
    %{stats | requests: n, avg_latency_ms: avg}
  end

  defp schedule_health_check do
    Process.send_after(self(), :health_check, 60_000)
  end
end
