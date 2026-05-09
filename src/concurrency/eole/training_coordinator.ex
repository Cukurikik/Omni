# @omni-layer Concurrency | @omni-source eole-nlp/eole
# @omni-description Distributed LM training coordinator in Elixir: GenServer-based
# gradient aggregation and model synchronization across nodes.
# @omni-lang Elixir | @omni-batch 16 | @omni-semester 16

defmodule Omni.Eole.TrainingCoordinator do
  use GenServer

  defstruct [:model_version, :n_workers, :accumulated_grads, :step_count, :learning_rate]

  def start_link(opts \\ []) do
    n_workers = Keyword.get(opts, :n_workers, 4)
    lr = Keyword.get(opts, :learning_rate, 0.001)
    GenServer.start_link(__MODULE__, %__MODULE__{
      model_version: 0, n_workers: n_workers,
      accumulated_grads: %{}, step_count: 0, learning_rate: lr
    }, name: __MODULE__)
  end

  @impl true
  def init(state), do: {:ok, state}

  @impl true
  def handle_call({:submit_gradients, worker_id, gradients}, _from, state) do
    new_grads = Map.put(state.accumulated_grads, worker_id, gradients)
    if map_size(new_grads) >= state.n_workers do
      aggregated = aggregate_gradients(Map.values(new_grads))
      new_state = %{state |
        accumulated_grads: %{},
        step_count: state.step_count + 1,
        model_version: state.model_version + 1
      }
      {:reply, {:ok, %{step: new_state.step_count, grad_norm: grad_norm(aggregated), version: new_state.model_version}}, new_state}
    else
      {:reply, {:waiting, map_size(new_grads), state.n_workers}, %{state | accumulated_grads: new_grads}}
    end
  end

  @impl true
  def handle_call(:get_status, _from, state) do
    {:reply, %{version: state.model_version, step: state.step_count, pending: map_size(state.accumulated_grads)}, state}
  end

  defp aggregate_gradients(grad_lists) do
    n = length(grad_lists)
    if n == 0, do: [], else: do
      first = hd(grad_lists)
      Enum.map(0..(length(first)-1), fn i ->
        Enum.reduce(grad_lists, 0.0, fn grads, acc ->
          acc + Enum.at(grads, i, 0.0)
        end) / n
      end)
    end
  end

  defp grad_norm(grads) do
    grads |> Enum.map(fn g -> g * g end) |> Enum.sum() |> :math.sqrt()
  end

  # Public API
  def submit_gradients(worker_id, gradients) do
    GenServer.call(__MODULE__, {:submit_gradients, worker_id, gradients})
  end

  def get_status, do: GenServer.call(__MODULE__, :get_status)
end
