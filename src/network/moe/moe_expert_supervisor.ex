# moe_expert_supervisor.ex — Fault-Tolerant Expert Process Supervisor
# Layer: Network / Concurrency — MoE Actor System (Elixir)
#
# OTP supervisor tree for MoE expert processes. Each expert runs as
# a GenServer with independent failure domains. Supervisors restart
# failed experts without affecting healthy ones.

defmodule Omni.MoE.ExpertSupervisor do
  @moduledoc """
  Supervises a pool of MoE expert processes.

  Each expert is an independent GenServer that processes tokens routed
  to it. If an expert crashes, only that expert is restarted — other
  experts continue processing without interruption.
  """
  use Supervisor

  def start_link(opts) do
    num_experts = Keyword.get(opts, :num_experts, 8)
    expert_dim = Keyword.get(opts, :expert_dim, 768)
    Supervisor.start_link(__MODULE__, {num_experts, expert_dim}, name: __MODULE__)
  end

  @impl true
  def init({num_experts, expert_dim}) do
    children =
      for expert_id <- 0..(num_experts - 1) do
        %{
          id: {:expert, expert_id},
          start: {Omni.MoE.ExpertWorker, :start_link,
                  [%{expert_id: expert_id, dim: expert_dim}]},
          restart: :permanent,
          shutdown: 5000,
          type: :worker
        }
      end

    # Add router process
    router_child = %{
      id: :router,
      start: {Omni.MoE.RouterProcess, :start_link, [num_experts]},
      restart: :permanent,
      type: :worker
    }

    # Add metrics collector
    metrics_child = %{
      id: :metrics,
      start: {Omni.MoE.MetricsCollector, :start_link, [num_experts]},
      restart: :permanent,
      type: :worker
    }

    Supervisor.init(
      [router_child, metrics_child | children],
      strategy: :one_for_one,
      max_restarts: 10,
      max_seconds: 60
    )
  end
end

defmodule Omni.MoE.ExpertWorker do
  @moduledoc """
  GenServer for a single MoE expert.

  Processes batches of tokens routed to this expert, maintains
  processing statistics, and reports health status.
  """
  use GenServer

  defstruct [:expert_id, :dim, :tokens_processed, :errors,
             :avg_latency_us, :is_ready, :created_at]

  def start_link(config) do
    GenServer.start_link(__MODULE__, config,
      name: via_tuple(config.expert_id))
  end

  def process_tokens(expert_id, tokens) do
    GenServer.call(via_tuple(expert_id), {:process, tokens}, 30_000)
  end

  def get_stats(expert_id) do
    GenServer.call(via_tuple(expert_id), :stats)
  end

  def health_check(expert_id) do
    GenServer.call(via_tuple(expert_id), :health)
  end

  # Server callbacks

  @impl true
  def init(config) do
    state = %__MODULE__{
      expert_id: config.expert_id,
      dim: config.dim,
      tokens_processed: 0,
      errors: 0,
      avg_latency_us: 0,
      is_ready: true,
      created_at: System.monotonic_time(:millisecond)
    }
    {:ok, state}
  end

  @impl true
  def handle_call({:process, tokens}, _from, state) do
    start = System.monotonic_time(:microsecond)

    result =
      try do
        # Process tokens through expert FFN
        output = expert_forward(tokens, state.dim)
        {:ok, output}
      rescue
        e ->
          {:error, Exception.message(e)}
      end

    elapsed = System.monotonic_time(:microsecond) - start

    new_state = case result do
      {:ok, _} ->
        num_tokens = length(tokens)
        new_avg = update_ema(state.avg_latency_us, elapsed, 0.05)
        %{state |
          tokens_processed: state.tokens_processed + num_tokens,
          avg_latency_us: round(new_avg)}
      {:error, _} ->
        %{state | errors: state.errors + 1}
    end

    # Report to metrics collector
    Omni.MoE.MetricsCollector.report(
      state.expert_id, elapsed,
      elem(result, 0) == :ok)

    {:reply, result, new_state}
  end

  @impl true
  def handle_call(:stats, _from, state) do
    stats = %{
      expert_id: state.expert_id,
      tokens_processed: state.tokens_processed,
      errors: state.errors,
      avg_latency_us: state.avg_latency_us,
      uptime_ms: System.monotonic_time(:millisecond) - state.created_at
    }
    {:reply, stats, state}
  end

  @impl true
  def handle_call(:health, _from, state) do
    health = %{
      expert_id: state.expert_id,
      is_ready: state.is_ready,
      error_rate: error_rate(state),
      status: if(state.is_ready and error_rate(state) < 0.1, do: :healthy, else: :degraded)
    }
    {:reply, health, state}
  end

  defp via_tuple(expert_id) do
    {:via, Registry, {Omni.MoE.ExpertRegistry, {:expert, expert_id}}}
  end

  defp expert_forward(tokens, dim) do
    # Simulated expert computation
    # In production: calls into NIF for PyTorch/ONNX inference
    Enum.map(tokens, fn token ->
      :rand.uniform() * 0.01  # placeholder activation
    end)
  end

  defp update_ema(old_avg, new_val, alpha) do
    old_avg * (1 - alpha) + new_val * alpha
  end

  defp error_rate(state) do
    total = state.tokens_processed + state.errors
    if total == 0, do: 0.0, else: state.errors / total
  end
end

defmodule Omni.MoE.RouterProcess do
  @moduledoc """
  Central router process that dispatches tokens to expert workers.
  """
  use GenServer

  def start_link(num_experts) do
    GenServer.start_link(__MODULE__, num_experts, name: __MODULE__)
  end

  def route_batch(tokens, expert_assignments) do
    GenServer.call(__MODULE__, {:route, tokens, expert_assignments}, 60_000)
  end

  @impl true
  def init(num_experts) do
    {:ok, %{num_experts: num_experts, batches_routed: 0}}
  end

  @impl true
  def handle_call({:route, tokens, assignments}, _from, state) do
    # Group tokens by expert
    grouped = Enum.zip(tokens, assignments)
    |> Enum.group_by(fn {_token, expert_id} -> expert_id end)
    |> Enum.map(fn {expert_id, pairs} ->
      expert_tokens = Enum.map(pairs, fn {token, _} -> token end)
      {expert_id, expert_tokens}
    end)

    # Dispatch to expert workers in parallel
    tasks = Enum.map(grouped, fn {expert_id, expert_tokens} ->
      Task.async(fn ->
        {expert_id, Omni.MoE.ExpertWorker.process_tokens(expert_id, expert_tokens)}
      end)
    end)

    results = Task.await_many(tasks, 30_000)
    new_state = %{state | batches_routed: state.batches_routed + 1}
    {:reply, {:ok, results}, new_state}
  end
end

defmodule Omni.MoE.MetricsCollector do
  @moduledoc "Collects and aggregates expert performance metrics."
  use GenServer

  def start_link(num_experts) do
    GenServer.start_link(__MODULE__, num_experts, name: __MODULE__)
  end

  def report(expert_id, latency_us, success) do
    GenServer.cast(__MODULE__, {:report, expert_id, latency_us, success})
  end

  def get_all_metrics do
    GenServer.call(__MODULE__, :get_all)
  end

  @impl true
  def init(num_experts) do
    metrics = for e <- 0..(num_experts - 1), into: %{} do
      {e, %{total: 0, errors: 0, latency_sum: 0}}
    end
    {:ok, metrics}
  end

  @impl true
  def handle_cast({:report, expert_id, latency_us, success}, metrics) do
    updated = Map.update!(metrics, expert_id, fn m ->
      %{m |
        total: m.total + 1,
        errors: if(success, do: m.errors, else: m.errors + 1),
        latency_sum: m.latency_sum + latency_us}
    end)
    {:noreply, updated}
  end

  @impl true
  def handle_call(:get_all, _from, metrics) do
    {:reply, metrics, metrics}
  end
end
