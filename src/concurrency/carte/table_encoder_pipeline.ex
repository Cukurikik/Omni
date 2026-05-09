# @omni-layer Concurrency | @omni-source soda-inria/carte | @omni-lang Elixir
# @omni-description Distributed table encoding pipeline in Elixir: GenServer for
# parallel row encoding with graph transformer across multiple nodes.
defmodule Omni.Carte.TableEncoder do
  use GenServer

  defstruct [:d_model, :n_workers, :pending, :completed, :stats]

  def start_link(opts \\ []) do
    d = Keyword.get(opts, :d_model, 128)
    w = Keyword.get(opts, :n_workers, 4)
    GenServer.start_link(__MODULE__, %__MODULE__{
      d_model: d, n_workers: w, pending: [], completed: [], stats: %{total: 0, errors: 0}
    }, name: __MODULE__)
  end

  @impl true
  def init(state), do: {:ok, state}

  @impl true
  def handle_call({:encode_row, row_data}, _from, state) do
    embedding = encode_single_row(row_data, state.d_model)
    new_completed = [embedding | state.completed]
    new_stats = %{state.stats | total: state.stats.total + 1}
    {:reply, {:ok, embedding}, %{state | completed: new_completed, stats: new_stats}}
  end

  @impl true
  def handle_call(:get_stats, _from, state) do
    {:reply, state.stats, state}
  end

  defp encode_single_row(row_data, d_model) do
    Enum.map(0..(d_model-1), fn j ->
      Enum.reduce(row_data, 0.0, fn {_k, v}, acc ->
        val = if is_number(v), do: v * 0.001, else: :erlang.phash2(v, 10000) * 0.0001
        acc + :math.sin((j + 1) * val)
      end)
    end)
  end

  def encode_row(row), do: GenServer.call(__MODULE__, {:encode_row, row})
  def stats, do: GenServer.call(__MODULE__, :get_stats)
end
