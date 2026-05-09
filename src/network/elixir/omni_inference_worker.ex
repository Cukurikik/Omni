# OMNI Network — Elixir GenServer Inference Worker
# Concurrent inference processing with OTP supervision.

defmodule Omni.Inference.Worker do
  use GenServer
  require Logger

  defmodule State do
    defstruct [:id, :model_id, :endpoint, :stats, :status]
  end

  defmodule Stats do
    defstruct total: 0, errors: 0, total_latency_ms: 0.0

    def record(stats, latency_ms) do
      %{stats | total: stats.total + 1, total_latency_ms: stats.total_latency_ms + latency_ms}
    end

    def record_error(stats) do
      %{stats | errors: stats.errors + 1}
    end

    def avg_latency(stats) do
      if stats.total > 0, do: stats.total_latency_ms / stats.total, else: 0.0
    end
  end

  # Client API
  def start_link(opts) do
    id = Keyword.get(opts, :id, :rand.uniform(10000))
    GenServer.start_link(__MODULE__, opts, name: via(id))
  end

  def infer(worker_id, prompt, opts \\ []) do
    GenServer.call(via(worker_id), {:infer, prompt, opts}, 30_000)
  end

  def get_stats(worker_id) do
    GenServer.call(via(worker_id), :stats)
  end

  def health(worker_id) do
    GenServer.call(via(worker_id), :health)
  end

  # Server Callbacks
  @impl true
  def init(opts) do
    state = %State{
      id: Keyword.get(opts, :id, 0),
      model_id: Keyword.get(opts, :model_id, "omni-7b"),
      endpoint: Keyword.get(opts, :endpoint, "http://localhost:9090"),
      stats: %Stats{},
      status: :ready
    }
    Logger.info("Inference worker #{state.id} started (model=#{state.model_id})")
    {:ok, state}
  end

  @impl true
  def handle_call({:infer, prompt, opts}, _from, state) do
    start = System.monotonic_time(:millisecond)
    max_tokens = Keyword.get(opts, :max_tokens, 256)
    temperature = Keyword.get(opts, :temperature, 0.7)

    case do_inference(state.endpoint, prompt, max_tokens, temperature) do
      {:ok, result} ->
        latency = System.monotonic_time(:millisecond) - start
        new_stats = Stats.record(state.stats, latency)
        {:reply, {:ok, Map.put(result, :latency_ms, latency)}, %{state | stats: new_stats}}

      {:error, reason} ->
        new_stats = Stats.record_error(state.stats)
        {:reply, {:error, reason}, %{state | stats: new_stats}}
    end
  end

  @impl true
  def handle_call(:stats, _from, state) do
    result = %{
      worker_id: state.id,
      model_id: state.model_id,
      total_requests: state.stats.total,
      errors: state.stats.errors,
      avg_latency_ms: Stats.avg_latency(state.stats),
      status: state.status
    }
    {:reply, result, state}
  end

  @impl true
  def handle_call(:health, _from, state) do
    {:reply, %{status: state.status, worker_id: state.id}, state}
  end

  defp do_inference(endpoint, prompt, max_tokens, temperature) do
    body = Jason.encode!(%{
      prompt: prompt,
      max_tokens: max_tokens,
      temperature: temperature
    })

    case :httpc.request(
      :post,
      {~c"#{endpoint}/infer", [], ~c"application/json", body},
      [{:timeout, 30_000}],
      []
    ) do
      {:ok, {{_, 200, _}, _, response_body}} ->
        {:ok, Jason.decode!(to_string(response_body))}
      {:ok, {{_, code, _}, _, _}} ->
        {:error, "HTTP #{code}"}
      {:error, reason} ->
        {:error, inspect(reason)}
    end
  end

  defp via(id), do: {:via, Registry, {Omni.Inference.Registry, id}}
end
