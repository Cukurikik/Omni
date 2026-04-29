defmodule Omni.Concurrency.MLExplain.ExplanationSupervisor do
  use Supervisor

  def start_link(init_arg) do
    Supervisor.start_link(__MODULE__, init_arg, name: __MODULE__)
  end

  @impl true
  def init(_init_arg) do
    children = [
      {Omni.Concurrency.MLExplain.KernelWorker, name: :kernel_w1},
      {Omni.Concurrency.MLExplain.KernelWorker, name: :kernel_w2}
    ]

    Supervisor.init(children, strategy: :one_for_one)
  end
end

defmodule Omni.Concurrency.MLExplain.KernelWorker do
  use GenServer

  def start_link(opts) do
    GenServer.start_link(__MODULE__, :ok, opts)
  end

  @impl true
  def init(:ok) do
    {:ok, %{active_jobs: 0}}
  end

  @impl true
  def handle_call({:compute_kernel, data_vector}, _from, state) do
    if length(data_vector) == 0 do
      {:reply, {:error, "Empty data vector"}, state}
    else
      # Math logic: Kernel weights calculation
      weight = Enum.reduce(data_vector, 0.0, fn x, acc -> acc + :math.exp(-x * x) end)
      
      new_state = %{state | active_jobs: state.active_jobs + 1}
      {:reply, {:ok, %{kernel_weight: weight}}, new_state}
    end
  end
end
