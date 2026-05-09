# @omni-layer Concurrency | @omni-source huggingface/text-generation-inference
# @omni-description Request queue manager in Elixir: continuous batching with
# dynamic batch assembly and priority scheduling for TGI.
# @omni-lang Elixir | @omni-batch 16 | @omni-semester 16
defmodule Omni.TGI.RequestQueue do
  use GenServer

  defstruct [:max_batch, :max_tokens, :queue, :active_batch, :stats]

  def start_link(opts \\ []) do
    GenServer.start_link(__MODULE__, %__MODULE__{
      max_batch: Keyword.get(opts, :max_batch, 32),
      max_tokens: Keyword.get(opts, :max_tokens, 2048),
      queue: :queue.new(),
      active_batch: nil,
      stats: %{total_requests: 0, total_tokens: 0, batches_served: 0}
    }, name: __MODULE__)
  end

  @impl true
  def init(state), do: {:ok, state}

  @impl true
  def handle_call({:enqueue, request}, _from, state) do
    new_queue = :queue.in(request, state.queue)
    new_stats = %{state.stats | total_requests: state.stats.total_requests + 1}
    {:reply, {:ok, :queue.len(new_queue)}, %{state | queue: new_queue, stats: new_stats}}
  end

  @impl true
  def handle_call(:assemble_batch, _from, state) do
    {batch, remaining} = take_batch(state.queue, state.max_batch, state.max_tokens)
    if length(batch) == 0 do
      {:reply, {:empty}, state}
    else
      total_toks = Enum.reduce(batch, 0, fn req, acc -> acc + Map.get(req, :n_tokens, 1) end)
      new_stats = %{state.stats |
        total_tokens: state.stats.total_tokens + total_toks,
        batches_served: state.stats.batches_served + 1
      }
      {:reply, {:ok, batch, total_toks}, %{state | queue: remaining, stats: new_stats}}
    end
  end

  @impl true
  def handle_call(:stats, _from, state), do: {:reply, state.stats, state}

  defp take_batch(queue, max_batch, max_tokens) do
    take_batch(queue, max_batch, max_tokens, [], 0)
  end
  defp take_batch(queue, 0, _max_tokens, acc, _total), do: {Enum.reverse(acc), queue}
  defp take_batch(queue, remaining, max_tokens, acc, total) do
    case :queue.out(queue) do
      {{:value, item}, rest} ->
        toks = Map.get(item, :n_tokens, 1)
        if total + toks > max_tokens, do: {Enum.reverse(acc), queue},
        else: take_batch(rest, remaining - 1, max_tokens, [item | acc], total + toks)
      {:empty, _} -> {Enum.reverse(acc), queue}
    end
  end

  def enqueue(request), do: GenServer.call(__MODULE__, {:enqueue, request})
  def assemble_batch, do: GenServer.call(__MODULE__, :assemble_batch)
  def stats, do: GenServer.call(__MODULE__, :stats)
end
