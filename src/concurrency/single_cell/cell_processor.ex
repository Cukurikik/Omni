defmodule Omni.Concurrency.SingleCell.CellProcessor do
  use Supervisor

  def start_link(init_arg) do
    Supervisor.start_link(__MODULE__, init_arg, name: __MODULE__)
  end

  @impl true
  def init(_init_arg) do
    children = [
      %{
        id: UMAPWorker,
        start: {Omni.Concurrency.SingleCell.UMAPWorker, :start_link, []},
        type: :worker
      }
    ]

    Supervisor.init(children, strategy: :one_for_one, max_restarts: 5)
  end
end

defmodule Omni.Concurrency.SingleCell.UMAPWorker do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{}, name: __MODULE__)
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_call({:project_cell, cell_vector}, _from, state) do
    if length(cell_vector) == 0 do
      {:reply, {:error, "Empty cell vector"}, state}
    else
      # Deterministic UMAP projection math projection
      x = Enum.sum(cell_vector) / length(cell_vector)
      y = :math.sin(x) * 10.0
      {:reply, {:ok, {x, y}}, state}
    end
  end
end
