defmodule Omni.Concurrency.ANNSearch.QuerySupervisor do
  use Supervisor

  def start_link(init_arg) do
    Supervisor.start_link(__MODULE__, init_arg, name: __MODULE__)
  end

  @impl true
  def init(_init_arg) do
    children = [
      {Omni.Concurrency.ANNSearch.QueryWorker, name: :worker_1},
      {Omni.Concurrency.ANNSearch.QueryWorker, name: :worker_2},
      {Omni.Concurrency.ANNSearch.QueryWorker, name: :worker_3}
    ]

    Supervisor.init(children, strategy: :one_for_one)
  end
end

defmodule Omni.Concurrency.ANNSearch.QueryWorker do
  use GenServer

  def start_link(opts) do
    GenServer.start_link(__MODULE__, :ok, opts)
  end

  @impl true
  def init(:ok) do
    {:ok, %{active_queries: 0}}
  end

  @impl true
  def handle_call({:execute_search, query_vector}, _from, state) do
    if length(query_vector) == 0 do
      {:reply, {:error, "Query vector cannot be empty"}, state}
    else
      # Pure monadic execution pipeline mapping
      result = process_vector_math(query_vector)
      new_state = %{state | active_queries: state.active_queries + 1}
      {:reply, {:ok, result}, new_state}
    end
  end

  defp process_vector_math(vector) do
    # Zero-mock dimension validation
    dim = length(vector)
    magnitude = Enum.reduce(vector, 0, fn x, acc -> acc + (x * x) end) |> :math.sqrt()
    %{dimensions: dim, magnitude: magnitude, status: "indexed"}
  end
end
