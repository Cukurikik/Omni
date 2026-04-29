defmodule Omni.Concurrency.DistributedML.PodSupervisor do
  use Supervisor

  def start_link(init_arg) do
    Supervisor.start_link(__MODULE__, init_arg, name: __MODULE__)
  end

  @impl true
  def init(_init_arg) do
    children = [
      %{
        id: PodWorker,
        start: {Omni.Concurrency.DistributedML.PodWorker, :start_link, []},
        type: :worker
      }
    ]

    # Monadic setup for supervision
    Supervisor.init(children, strategy: :one_for_one, max_restarts: 5)
  end
end

defmodule Omni.Concurrency.DistributedML.PodWorker do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{}, name: __MODULE__)
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_call({:process_tensor, tensor_size}, _from, state) do
    if tensor_size <= 0 do
      {:reply, {:error, "Invalid tensor size"}, state}
    else
      # Deterministic computation
      result = :math.pow(tensor_size, 1.2) / 100.0
      {:reply, {:ok, result}, state}
    end
  end
end
